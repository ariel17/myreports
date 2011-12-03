#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from server.views import show_all_servers, show_server_id, show_server_ip, \
        show_server_name, test_connection


urlpatterns = patterns('',

    url(r'^$', show_all_servers, name='all_servers'),

    url(r'^(?P<id>\d+)/$', show_server_id, name='server_id'),

    url(r'^(?P<ip>[0-9\.]{7,15})/$', show_server_ip, name='server_ip'),

    url(r'^(?P<name>[\w\-]+)/$', show_server_name, name='server_name'),

    url(r'^test/$', test_connection, name='test_connection'),
)
