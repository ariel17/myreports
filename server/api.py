#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"

from server.models import Server, Database
from tastypie import fields
from tastypie.resources import ModelResource


class ServerResource(ModelResource):
    class Meta:
        queryset = Server.objects.all()
        resource_name = 'server'
        excludes = ['password', ]
        ordering = ['id', ]

        
class DatabaseResource(ModelResource):
    server = fields.ForeignKey(ServerResource, 'server')
    class Meta:
        queryset = Database.objects.all()
        resource_name = 'db'
        ordering = ['server', 'id']
