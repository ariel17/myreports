#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from report.views import show_report


urlpatterns = patterns('',

        url(r'^(?P<id>\d+)/$', show_report, name='show_report_id'),

        url(r'^(?P<name>[\w\-]+)/$', show_report,
            name='show_report_name'),

        url(r'^(?P<id>\d+)/(?P<server_id>\d+)/$', show_report,
            name='show_report_id_id'),
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<server_id>\d+)/$',
            show_report, name='show_report_name_id'),

        url(r'^(?P<id>\d+)/(?P<ip>[0-9\.]{7,15})/$', show_report,
            name='show_report_id_ip'),                  
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<ip>[0-9\.]{7,15})/$',
            show_report, name='show_report_name_ip'),

        url(r'^(?P<id>\d+)/(?P<server_name>[\w\-]+)/$',
            show_report, name='show_report_id_name'),                  

        url(r'^(?P<name>[\w\-]+)/(?P<server_name>[\w\-]+)/$',
            show_report, name='show_report_name_name'),
)
