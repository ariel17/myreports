#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description:
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import logging
from jsonrpclib import Server as JSONServer
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer


logger = logging.getLogger(__name__)


class RPCHandler(object):
    """
    """
    servers = {}

    def __init__(self, servers):
        super(RPCHandler, self).__init__()
        self.__servers_to_dict(servers)

    def __servers_to_dict(self, server_list):
        """
        Receives a list of Server objects and returns a dict with the same
        objects indexed by id.
        """
        for s in server_list:
            self.servers[s.id] = s

    def call_method(self, id, method, **kwargs):
        """
        """
        s = self.servers[id]
        return getattr(s, method)(**kwargs)
    

class RPCServer(SimpleJSONRPCServer):
    """
    """
    def __init__(self, mysql_servers, host, port):
        SimpleJSONRPCServer((host, port))
        self.register_instance(RPCHandler(mysql_servers))        


class RPCClient(JSONServer):
    """
    """
    def __init__(self, host, port):
        JSONServer("http://%s:%d" % (host, port))
