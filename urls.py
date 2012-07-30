#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: TODO
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from server.api import ServerResource, DatabaseResource
from server.views import test_connection
from tastypie.api import Api


admin.autodiscover()

api = Api(api_name='v1')
api.register(ServerResource())
api.register(DatabaseResource())

"""
TODO:

   Fix urls to this pattern:

   /direct/server/0123-4567-89AB/
   
   /direct/report/0123-4567-89AB/
   
   /reports/section/1/
   /reports/section/section-1/
   /reports/section/1/report-1/server-1/
   /direct/section/0123-4567-89AB/
"""


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # application patterns

    url(r'^report/servers/', include('server.urls')),

    url(r'^report/reports/', include('report.report_urls')),

    url(r'^report/sections/', include('report.section_urls')),

    url(r'^server/test/$', test_connection, name='test_connection'),

    url(r'^api/', include(api.urls)),

)
