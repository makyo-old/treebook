from forum.models import *
from forum.forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404

def view_forum(request, forum = '__root__'):
    return render_to_response('forum/forum_detail.html', context_instance = RequestContext(request, {'forum': get_object_or_404(Forum, slug = forum), 'posts': Post.objects.filter(forum__slug__exact = forum).filter(parent__isnull = True)}))

def view_topic(request, forum, post):
    p = get_object_or_404(Post, id = post)
    if p.parent is not None:
        return HttpResponseRedirect('/forums/%s/%s/#%s%s' % (forum, p.parent.id, p.id, request.GET.get('minimal', None) is None and '' or '?minimal=true'))
    if not p.forum.slug == forum:
        request.user.message_set.create(message = "<span class=\"error\">I couldn't find that post in the forum requested; this is the only post with that ID!</span>")
        return HttpResponseRedirect('/forums/%s/%s/' % (p.forum.slug, p.id))
    return render_to_response(request.GET.get('minimal', None) is not None and 'forum/post_detail_minimal.html' or 'forum/post_detail.html', context_instance = RequestContext(request, {'post': p}))

@login_required
def post_topic(request, forum):
    f = get_object_or_404(Forum, slug = forum)
    if not f.users_can_post and not request.user in f.moderators:
        return render_to_response('forum/error.html', context_instance = RequestContext(request, {'error': "Users may not post to this forum"}))
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            p = Post(forum = f, owner = request.user, title = form.cleaned_data['title'], body = form.cleaned_data['body'])
            p.save()
            return HttpResponseRedirect('/forums/%s/%s/' % (forum, p.id))
    else:
        moderator = False
        if request.user in f.moderators.all():
            moderator = True
        return render_to_response('forum/post_form.html', context_instance = RequestContext(request, {'form': form, 'is_moderator': moderator}))

@login_required
def post_reply(request, forum, post):
    # get forum and parent post objects
    f = get_object_or_404(Forum, slug = forum)
    post_parent = get_object_or_404(Post, id = post)

    # make sure we can post
    if (not f.users_can_post or not post_parent.users_can_reply) and not request.user in f.moderators.all():
        return render_to_response('forum/error.html', context_instance = RequestContext(request, {'error': "Users may not post to this forum"}))

    # If the parent post is not the topic post, redirect to the reply-to-topic-post
    if post_parent.parent is not None:
        return HttpResponseRedirect('/forums/%s/%s/reply/?reply-to=%s' % (f.slug, parent.parent.id, parent.id))

    # Get our form - if data was POSTed, save it, and return to the post, otherwise, show the form with prepopulated fields
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            p = Post(forum = f, parent = post_parent, owner = request.user, title = form.cleaned_data['title'], body = form.cleaned_data['body'])
            p.save()
            return HttpResponseRedirect('/forums/%s/%s/' % (forum, p.id))
    else:
        if request.GET.get('reply-to', None):
            quote = get_object_or_404(Post, id = request.GET['reply-to'])
            form = PostForm(initial = {'title': 'Re: %s' % quote.title, 'body': '[quote=%s]\n%s\n[/quote]\n\n' % (quote.owner.first_name is not None and quote.owner.get_full_name() or quote.owner.username, quote.body)})
        else:
            form = PostForm(initial = {'title': 'Re: %s' % post_parent.title})
        return render_to_response('forum/post_reply_form.html', context_instance = RequestContext(request, {'form': form, 'topic_url': '/forums/%s/%s/?minimal=true#%s' % (forum, post, request.GET.get('reply-to', post))}))

@login_required
def edit_topic(request, forum, post):
    f = get_object_or_404(Forum, slug = forum)
    if not f.users_can_post and not (request.user in f.moderators.all()):
        return render_to_response('forum/error.html', context_instance = RequestContext(request, {'error': "Users may not post to this forum"}))
    p = get_object_or_404(Post, id = post)
    if not (request.user in f.moderators.all() or request.user == p.owner):
        return render_to_response('forum/error.html', context_instance = RequestContext(request, {'error': "Only the owner of a post or moderators may edit this post."}))
    form = PostEditForm({'title': p.title, 'body': p.body})
    if request.method == 'POST':
        form = PostEditForm(request.POST)
        if form.is_valid():
            p.title = form.cleaned_data['title']
            p.body = form.cleaned_data['body']
            p.mreason = form.cleaned_data['reason']
            p.muser = request.user
            p.save()
            return HttpResponseRedirect('/forums/%s/%s' % (forum, p.id))
    else:
        return render_to_response('forum/post_edit_form.html', context_instance = RequestContext(request, {'form': form}))

@login_required
def delete_topic(request, forum, post):
    p = get_object_or_404(Post, id = post)
    f = get_object_or_404(Forum, slug = forum)
    if not (request.user in f.moderators.all() or request.user == p.owner):
        return render_to_response('forum/error.html', context_instance = RequestContext(request, {'error': 'Only the owner of the post or moderators may delete this post.'}))
    if not p.parent:
        for child in p.post_set.all():
            child.delete()
        request.user.message_set.create(message = '<div class="success">Topic replies deleted</div>')
    p.delete()
    request.user.message_set.create(message = '<div class="success">Post deleted</div>')
    return HttpResponseRedirect('/forums/%s/' % forum)


@login_required
def list_pms(request):
    from django.db.models import Q
    pms = None
    try:
        pms = PM.objects.filter(Q(parent__exact = None), Q(user_to__exact = request.user) | Q(user_from__exact = request.user))
    except:
        pms = None
    return render_to_response('forum/list_pms.html', context_instance = RequestContext(request, {'pms': pms}))

@login_required
def view_pm(request, post):
    pm = get_object_or_404(PM, id = post)
    if (pm.user_to == request.user) or (pm.user_from == request.user):
        if pm.parent is not None:
            return HttpResponseRedirect('/forums/pm/%s/#%s' % (pm.parent.id, pm.id))
        return render_to_response(request.GET.get('minimal', None) is None and 'forum/pm_detail.html' or 'forum/pm_detail_minimal.html', context_instance = RequestContext(request, {'post': pm}))
    else:
        raise Http404()

@login_required
def mark_pm_as_read(request, post):
    pm = get_object_or_404(PM, id = post)
    if pm.user_to == request.user:
        pm.is_read = True
        pm.save()
        return HttpResponseRedirect('/forums/pm/%s' % post)
    else:
        raise Http404()

@login_required
def reply_to_pm(request, post):
    pm = get_object_or_404(PM, id = post)
    if (pm.user_to == request.user) or (pm.user_from == request.user):
        form = PostForm(initial = {'title': 'RE: %s' % pm.title, 'body': '[quote=%s]%s[/quote]' % (pm.user_from.username, pm.body)})
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                newpm = PM(user_to = (pm.user_to == request.user and pm.user_from or request.user), 
                           user_from = request.user, parent = (pm.parent is None and pm or pm.parent), 
                           title = form.cleaned_data['title'], 
                           body = form.cleaned_data['body'],
                           is_read = False)
                newpm.save()
                return HttpResponseRedirect('/forums/pm/%s/' % (newpm.id))
        else:
            return render_to_response('forum/pm_reply_form.html', context_instance = RequestContext(request, {'pm': pm, 'form': form}))

    else:
        raise Http404

@login_required
def start_pm(request, user):
    u = get_object_or_404(User, username = user)
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            pm = PM(user_to = u, user_from = request.user, parent = None, title = form.cleaned_data['title'], body = form.cleaned_data['body'], is_read = False)
            pm.save()
            return HttpResponseRedirect('/forum/pm/%s/' % (pm.id))
    else:
        return render_to_response('forum/pm_post_form.html', context_instance = RequestContext(request, {'form': form, 'user_to': user}))

@login_required
def edit_sig(request):
    if not request.user.forumuser:
        f = ForumUser(user = request.user)
        f.save()
    if request.method == 'POST' and request.POST.get('signature', None) is not None:
        request.user.forumuser.signature = request.POST['signature']
        request.user.forumuser.save()
    return render_to_response('forum/edit_sig.html', context_instance = RequestContext(request, {'sig': ForumUser.objects.get(user = request.user).signature}))

