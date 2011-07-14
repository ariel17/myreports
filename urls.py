from django.conf.urls.defaults import patterns, include, url

from server.views import show_all_reports
from report.views import show_report
from report.views import show_section

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myreports.views.home', name='home'),
    # url(r'^myreports/', include('myreports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # application patterns

    (r'^server/(?P<ip>[0-9\.]{7,15})/$', show_all_reports),

    (r'^server/(?P<id>\d+)/$', show_all_reports),

    (r'^report/(?P<id>\d+)/$', show_report),

    (r'^report/section/(?P<id>\d+)/$', show_section),

)
