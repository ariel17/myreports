#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from views import show_report, show_section


urlpatterns = patterns('',

        url(r'^(?P<id>\d+)/$', show_all_reports, name='show_servers'),

        url(r'^(?P<name>[\w\-]+)/$', show_all_reports, name='show_servers'),

        url(r'^(?P<id>\d+)/(?P<server_id>\d+)/$', show_all_reports, name='show_report_server'),
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<server_id>\d+)/$', show_all_reports, name='show_report_server'),

        url(r'^(?P<id>\d+)/(?P<ip>[0-9\.]{7,15})/$', show_all_reports, name='show_report_server'),                  
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<ip>[0-9\.]{7,15})/$', show_all_reports, name='show_report_server'),

        url(r'^(?P<id>\d+)/(?P<server_name>[\w\-]+)/$', show_all_reports, name='show_report_server'),                  
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<server_name>[\w\-]+)/$', show_all_reports, name='show_report_server'),

        url(r'^(?P<rbs_id>\d+)/$', show_report, name='show_report'),

        url(r'^(?P<rbs_id>\d+)/(?P<s_id>\d+)/$', show_section, name='show_section'),
)
