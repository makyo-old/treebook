from ebook.models import *
from usermgmt.models import *
from tagging.models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

def show_author(request, author):
    a = get_object_or_404(Author, user__username = author)
    bs = []
    for book in a.user.book_set.all():
        if book.published:
            bs.append(book)
        else:
            if request.user in book.authors.all():
                bs.append(book)
    if request.user.is_authenticated and request.user.author in a.friends.all():
        friend = True
    else:
        friend = False
    return render_to_response("author/show.html", context_instance = RequestContext(request, {'author': a, 'books': bs, 'friend': friend}))

def by_interest(request, tag):
    t = get_object_or_404(Tag, name = tag)
    p = Paginator(TaggedItem.objects.get_by_model(Author, t), 15)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        authors = p.page(page)
    except (EmptyPage, InvalidPage):
        authors = p.page(p.num_pages)
    return render_to_response("author/list.html", context_instance = RequestContext(request, {'authors': authors, 'title': "Authors interested in %s" % tag}))

def all_authors(request):
    p = Paginator(Author.objects.all(), 15)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        authors = p.page(page)
    except (EmptyPage, InvalidPage):
        authors = p.page(p.num_pages)
    return render_to_response("author/list.html", context_instance = RequestContext(request, {'authors': authors, 'title': "All authors"}))

@login_required
def edit_author(request, author):
    a = get_object_or_404(Author, user__username = author)
    if request.user == a.user:
        if request.method == "POST":
            a.bio = request.POST.get('bio', None) is None and a.bio or request.POST['bio']
            a.tags = request.POST.get('tags', None) is None and a.tags or request.POST['tags']
            a.save()
            return HttpResponseRedirect(a.get_absolute_url())
        else:
            return render_to_response("author/edit.html", context_instance = RequestContext(request, {'author': a}))
    else:
        raise Http404

def friends_list(request, author):
    a = get_object_or_404(Author, user__username = author)
    m = a.user.book_set.all()
    for friend in a.friends.all():
        m = m | friend.user.book_set.all()
    m = m.order_by('-ctime')
    ms = []
    for book in m:
        if book.published:
            ms.append(book)
        else:
            if request.user in book.authors.all():
                ms.append(book)
    p = Paginator(ms, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        manifestos = p.page(page)
    except (EmptyPage, InvalidPage):
        manifestos = p.page(p.num_pages)
    return render_to_response("manifesto/list.html", context_instance = RequestContext(request, {'manifestos': manifestos, 'title': "%s's friends list" % author}))

@login_required
def friend_author(request, author):
    a = get_object_or_404(Author, user__username = author)
    request.user.author.friends.add(a)
    request.user.message_set.create(message = '<div class="success">Successfully added %s as a friend!</div>' % author)
    if request.user.author not in a.friends.all():
        a.user.message_set.create(message = '<div class="success">%s added you as a friend! <a href="/a/%s/friend/">Add them as a friend</a></div>' % (request.user.username, request.user.username))
    return HttpResponseRedirect(a.get_absolute_url())

@login_required
def defriend_author(request, author):
    a = get_object_or_404(Author, user__username = author)
    if request.GET.get('confirm', None) == 'yes':
        request.user.author.friends.remove(a)
        request.user.author.save()
        request.user.message_set.create(message = '<div class="success">Successfully defriended %s</div>' % author)
        return HttpResponseRedirect(a.get_absolute_url())
