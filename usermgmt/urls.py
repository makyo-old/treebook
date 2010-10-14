from django.conf.urls.defaults import *

urlpatterns = patterns('usermgmt.views',
        (r'^(?P<author>[a-zA-Z0-9_]+)/$', 'show_author'),
        (r'^(?P<author>[a-zA-Z0-9_]+)/edit/$', 'edit_author'),
        (r'^(?P<author>[a-zA-Z0-9_]+)/friends/$', 'friends_list'),
        (r'^(?P<author>[a-zA-Z0-9_]+)/friend/$', 'friend_author'),
        (r'^(?P<author>[a-zA-Z0-9_]+)/defriend/$', 'defriend_author'),
)
