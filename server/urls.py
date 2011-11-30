#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from server.views import show_all_reports, test_connection


urlpatterns = patterns('',

    url(r'^(?P<id>\d+)/$', show_all_reports, name='show_reports'),

    url(r'^(?P<ip>[0-9\.]{7,15})/$', show_all_reports, name='show_reports'),

    url(r'^(?P<name>[\w\-]+)/$', show_all_reports, name='show_reports'),

    url(r'^test/$', test_connection, name='test_connection'),
)
