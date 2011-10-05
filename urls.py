from django.conf.urls.defaults import patterns, include, url
from report.views import show_report
from report.views import show_section

from tastypie.api import Api
from server.api import ServerResource, DatabaseResource

api = Api(api_name='v1')
api.register(ServerResource())
api.register(DatabaseResource())


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # application patterns

    url(r'^server/', include('server.urls')),

    url(r'^api/', include(api.urls)),

    url(r'^direct/', include('report.urls')),

)
