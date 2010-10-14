from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        (r'^(a|author)/', include('usermgmt.urls')),
        (r'^comments/', include('django.contrib.comments.urls')),
        (r'^(f|forums)/', include('forum.urls')),
        (r'^authors/$', 'usermgmt.views.all_authors'),
        (r'^interest/(?P<tag>[^/]+)/$', 'usermgmt.views.by_interest'),

        # user management
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
        (r'^accounts/register/$', 'usermgmt.account_views.create'),
        (r'^accounts/profile/$', 'usermgmt.account_views.show'),
        (r'^accounts/profile/update/$', 'usermgmt.account_views.update'),
        (r'^accounts/password/change/$', 'django.contrib.auth.views.password_change'),
        (r'^accounts/password/change/done/$', 'django.contrib.auth.views.password_change_done'),
        (r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset'),
        (r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
        (r'^accounts/password/reset/complete', 'django.contrib.auth.views.password_reset_complete'),
        (r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),

        (r'^admin/', include(admin.site.urls)),

        # everything else goes to ebooks
        ('^', include('ebook.urls')),
)
