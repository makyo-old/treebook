from django.conf.urls.defaults import *

urlpatterns = patterns('forum.views',
        (r'^pm/$', 'list_pms'),
        (r'^pm/(?P<post>\d+)/$', 'view_pm'),
        (r'^pm/(?P<post>\d+)/reply/$', 'reply_to_pm'),
        (r'^pm/(?P<post>\d+)/read/$', 'mark_pm_as_read'),
        (r'^pm/(?P<user>[-_a-zA-Z0-9]+)/$', 'start_pm'),
        (r'^signature/$', 'edit_sig'),

        (r'^$', 'view_forum'),
        (r'^(?P<forum>[-_a-z0-9]+)/$', 'view_forum'),
        (r'^(?P<forum>[-_a-z0-9]+)/post/$', 'post_topic'),
        (r'^(?P<forum>[-_a-z0-9]+)/(?P<post>\d+)/$', 'view_topic'),
        (r'^(?P<forum>[-_a-z0-9]+)/(?P<post>\d+)/reply/$', 'post_reply'),
        (r'^(?P<forum>[-_a-z0-9]+)/(?P<post>\d+)/edit/$', 'edit_topic'),
        (r'^(?P<forum>[-_a-z0-9]+)/(?P<post>\d+)/delete/$', 'delete_topic'),
        )
