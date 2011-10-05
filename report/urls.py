#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from views import show_report, show_section


urlpatterns = patterns('',

    url(r'^(?P<uuid>[\w-]+)/$', show_report, name='show_report'),

    url(r'^(?P<uuid>[\w-]+)/(?P<id>\d+)/$', show_section, name='show_section'),
)
