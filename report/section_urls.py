#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.conf.urls.defaults import patterns, url
from report.views import show_section


urlpatterns = patterns('',

        url(r'^(?P<id>\d+)/$', show_section, name='show_section_id'),

        url(r'^(?P<name>[\w\-]+)/$', show_section,
            name='show_section_name'),

        url(r'^(?P<id>\d+)/(?P<report_id>\d+)/$', show_section,
            name='show_section_id_id'),
                                                                             
        url(r'^(?P<name>[\w\-]+)/(?P<report_id>\d+)/$',
            show_section, name='show_section_name_id'),
)
