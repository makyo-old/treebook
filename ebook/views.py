from ebook.models import *
from ebook.forms import *
from usermgmt.models import *
from tagging.models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

@login_required
def create_chapter(request):
    form = ChapterForm()
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            c = form.save(commit = False)
            c.authors.add(request.user)
            #XXX fix for chapters
            #c.weight = request.user.book_set.count() + 1
            c.views = 0
            if c.friends_only:
                c.users_only = True
            m.save()
            form.save_m2m()
            return HttpResponseRedirect(m.get_absolute_url())
    return render_to_response("ebook/edit.html", context_instance = RequestContext(request, {'form': form}))

def read_chapter(request, chapter_id, comment_id = None):
    c = get_object_or_404(Chapter, id = chapter_id)
    if comment_id is not None:
        return HttpResponseRedirect("%s#c%s" % (c.get_absolute_url(), comment_id))
    if request.GET.get('c', None) is not None:
        return HttpResponseRedirect("%s#c%s" % (c.get_absolute_url(), request.GET['c']))
    if not c.published and request.user not in c.authors.all():
        raise Http404
    if c.users_only and not request.user.is_authenticated():
        return render_to_response("ebook/permission_denied.html", {'reason': "Post is viewable by logged-in users only"})
    if c.friends_only and not request.user not in c.owner.author.friends.all():
        can_see = False
        for a in c.authors.all():
            if request.user in a.author.friends.all():
                can_see = True
                break
        if not can_see:
            return render_to_response("ebook/permission_denied.html", {'reason': "Post is marked friends-only"})
    if request.user not in c.authors.all():
        m.views += 1
        m.save()
    return render_to_response("ebook/show.html", context_instance = RequestContext(request, {'chapter': c, 'cform': CommentForm()}))

@login_required
def update_chapter(request, chapter_id):
    c = get_object_or_404(Chapter, id = chapter_id)
    if request.method == "POST" and (request.user in c.authors.all() or request.user.is_staff()):
        form = ChapterForm(request.POST, instance = c)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(c.get_absolute_url())
    form = ChapterForm(instance = c)
    return render_to_response("ebook/edit.html", context_instance = RequestContext(request, {'form': form}))

@login_required
def rate_chapter(request, chapter_id, stars):
    c = get_object_or_404(Chapter, id = chapter_id)
    for r in request.user.rating_set.all():
        if r.chapter == c:
            request.user.message_set.create(message = '<div class="failure">You may only rate a chapter once!</div>')
            return HttpResponseRedirect(c.get_absolute_url())
    request.user.rating_set.create(chapter = c, stars = stars)
    cnt = 0
    sum = 0
    for r in c.user_rating.all():
        sum += r.stars
        cnt += 1
    c.stars = str(sum / cnt)
    c.save()
    request.user.message_set.create(message = '<div class="success">Chapter successfully rated</div>')
    return HttpResponseRedirect(c.get_absolute_url())

@login_required
def delete_chapter(request, chapter_id):
    c = get_object_or_404(Chapter, id = chapter_id)
    if c.authors.count() == 1:
        if request.GET.get('confirm', None) == 'yes' and (request.user in c.authors.all() or request.user.is_staff()):
            b = c.book
            c.delete()
            _reweight_posts(b)
            request.user.message_set.create(message = '<div class="success">Chapter successfully deleted</div>')
            return HttpResponseRedirect("/")
    else:
        c.authors.remove(request.user)
        c.published = False
        for a in c.authors.all():
            a.message_set.create(message = '<div class="warning">%(deletor)s has requested the deletion of the chapter <a href="%(url)s">%(chapter)s</a>.  It has been made private for now; you may confirm the deletion by visiting the chapter and deleting it from there, or you may edit the chapter to fix any problems and make it public again.</div>')
        request.user.message_set.create(message = '<div class="warning">Deletion has been requested of the other authors, the chapter has been made private, and your name has been removed from the list of authors.  The chapter will only be deleted when every author has approved it</div>')
    return render_to_response("ebook/permission_denied.html", {'reason': "Error deleting post - perhaps it's not yours?"})
    
@login_required
def feature_book(request, book_slug):
    b = get_object_or_404(Book, slug = book_slug)
    if request.GET.get('confirm', None) == 'yes' and request.user.is_staff:
        b.featured = True
        b.save()
        request.user.message_set.create(message = '<div class="success">Book successfully featured</div>')
        for a in b.authors.all():
            a.message_set.create(message = '<div class="success">Your book, %s, has been featured by HTR; congratulations!</div>' % b.title)
        return HttpResponseRedirect("/")
    return render_to_response("ebook/permission_denied.html", {'reason': "Error featuring post - perhaps you're not a staff member?"})

def by_tag(request, tag):
    t = get_object_or_404(Tag, name = tag)
    bs = []
    for book in TaggedItem.objects.get_by_model(Book, t):
        if book.published:
            bs.append(book)
        else:
            if request.user in book.authors.all():
                bs.append(book)
    p = Paginator(bs, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        books = p.page(page)
    except (EmptyPage, InvalidPage):
        books = p.page(p.num_pages)
    return render_to_response("ebook/list.html", context_instance = RequestContext(request, {'books': books, 'title': "Books tagged '%s'" % tag}))

def special_featured(request):
    bs = []
    for book in Book.objects.filter(featured = True).order_by('-ctime'):
        if book.published:
            bs.append(book)
        else:
            if request.user in book.authors.all():
                bs.append(book)
    p = Paginator(bs, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        books = p.page(page)
    except (EmptyPage, InvalidPage):
        books = p.page(p.num_pages)
    return render_to_response("ebook/list.html", context_instance = RequestContext(request, {'books': books, 'title': "Featured Books"}))

def special_high_rating(request):
    bs = []
    for book in sorted(Book.objects.all(), key = lambda b: b.aggregate_stars):
        if book.stars != 0.00:
            if book.published:
                bs.append(book)
            else:
                if request.user in book.authors.all():
                    bs.append(book)
    p = Paginator(bs, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        books = p.page(page)
    except (EmptyPage, InvalidPage):
        books = p.page(p.num_pages)
    return render_to_response("ebook/list.html", context_instance = RequestContext(request, {'books': books, 'title': "Highest Rated Books"}))

def special_recent(request):
    bs = []
    for book in Book.objects.order_by('-ctime'):
        if book.published:
            bs.append(book)
        else:
            if request.user in book.authors.all():
                bs.append(book)
    p = Paginator(bs, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        books = p.page(page)
    except (EmptyPage, InvalidPage):
        books = p.page(p.num_pages)
    return render_to_response("ebook/list.html", context_instance = RequestContext(request, {'books': books, 'title': "Recent Books"}))

@login_required
def post_comment(request, manifesto_id, parent_comment_id = None):
    form = CommentForm()
    m = get_object_or_404(Manifesto, id = manifesto_id)
    if parent_comment_id:
        p = get_object_or_404(Comment, id = parent_comment_id)
    else:
        p = None
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit = False)
            c.owner = request.user
            c.post = m
            c.parent = p
            if m.screen_comments and request.user != m.owner:
                c.published = False
                request.user.message_set.create(message = '<div id="warning">Comments are screened; when the author reviews your comment, it will show up</div>')
            else:
                c.published = True
            c.save()
            request.user.message_set.create(message = '<div id="success">Comment posted</div>')
            return HttpResponseRedirect(c.get_absolute_url())
    return HttpResponseRedirect(m.get_absolute_url())

@login_required
def delete_comment(request, comment_id):
    c = get_object_or_404(Comment, id = comment_id)
    if request.GET.get("confirm", None) == "yes" and (request.user == c.owner or request.user == c.post.owner or request.user.is_staff()):
        m = c.post
        c.delete()
        request.user.message_set.create(message = '<div class="success">Comment successfully deleted</div>')
        return HttpResponseRedirect(m.get_absolute_url())
    return render_to_response("ebook/permission_denied.html", {'reason': "Error deleting comment - perhaps it's not yours?"})

def _reweight_posts(book):
    i = 1
    for c in book.chapter_set.filter(parent__isnull = True):
        c.weight = i
        c.save()
        _reweight_subposts(c)
        i += 1

def _reweight_subposts(chapter):
    i = 1
    for c in chapter.chapter_set.all():
        c.weight = i
        c.save()
        _reweight_subposts(c)
        i += 1
