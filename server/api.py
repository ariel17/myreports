#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"

from tastypie.resources import ModelResource
from tastypie import fields
from server.models import Server, Database


class ServerResource(ModelResource):
    class Meta:
        queryset = Server.objects.all()
        resource_name = 'server'
        excludes = ['password', ]

        
class DatabaseResource(ModelResource):
    server = fields.ForeignKey(ServerResource, 'server')
    class Meta:
        queryset = Database.objects.all()
        resource_name = 'db'
