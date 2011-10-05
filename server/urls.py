#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from server.views import show_all_reports


urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', show_all_reports, name='show_all_reports'),
)
