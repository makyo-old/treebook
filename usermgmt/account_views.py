from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from usermgmt.models import *

def create(request):
    #
    if request.method == 'POST': 
        if request.POST.get('username', None) and request.POST.get('password', None) and request.POST.get('email', None):
            user = User.objects.create_user(request.POST['username'], request.POST['email'], None)
            user.set_password(request.POST['password'])
            user.save()
            author = Author(user = user)
            author.save()
            return HttpResponseRedirect('/accounts/login/')
        else:
            request.user.message_set.create(message = '<div class="failure">Oops!  All fields required!</div>')
    return render_to_response("registration/create_user.html", context_instance = RequestContext(request, {}))

@login_required
def show(request):
    #
    return render_to_response("registration/profile_show.html", context_instance = RequestContext(request, {}))

@login_required
def update(request):
    #
    if request.method == 'POST':
        request.user.first_name = request.POST.get('firstname', None) or request.user.first_name
        request.user.last_name = request.POST.get('lastname', None) or request.user.last_name
        request.user.email = request.POST.get('email', None) or request.user.email
        request.user.save()
    return HttpResponseRedirect('/accounts/profile/')
