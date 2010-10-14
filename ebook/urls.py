from django.conf.urls.defaults import *

urlpatterns = patterns('ebook.views',
        (r'^/$', 'special_recent'),
        (r'^featured/$', 'special_featured'),
        (r'^highest-rated/$', 'special_high_rating'),
        (r'^recent/$', 'special_recent'),
        (r'^new/$', 'create_manifesto'),
        (r'^(?P<manifesto_id>\d+)/feature/$', 'feature_manifesto'),
        (r'^(?P<manifesto_id>\d+)/edit/$', 'update_manifesto'),
        (r'^(?P<manifesto_id>\d+)/rate/(?P<stars>[1-5])/$', 'rate_manifesto'),
        (r'^(?P<manifesto_id>\d+)/delete/$', 'delete_manifesto'),
        (r'^(?P<manifesto_id>\d+)/((?P<parent_comment_id>\d+)/)?reply/$', 'post_comment'),
        (r'^(?P<manifesto_id>\d+)/(?P<comment_id>\d+)/delete/', 'delete_comment'),
        (r'^(?P<manifesto_id>\d+)/((?P<comment_id>\d+)/)?$', 'read_manifesto'),
        #(r'^tags/$', 'tag_cloud')
        (r'^tag/(?P<tag>[^/]+)/$', 'by_tag')
        )
