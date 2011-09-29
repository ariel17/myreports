#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description:
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import logging


logger = logging.getLogger(__name__)


class RPCHandler(object):
    """
    """
    def __init__(self, servers):
        super(RPCHandler, self).__init__()
        self.servers = RPCHandler.servers_to_dict(servers)

    @staticmethod
    def servers_to_dict(self, servers_list):
        """
        Receives a list of Server objects and returns a dict with the same
        objects indexed by id.
        """
        d = {}
        for s in servers_list:
            d[s.id] = s
        return d

    def call_method(self, id, method, **kwargs):
        """
        """
        s = self.servers[id]
        return getattr(s, method)(**kwargs)
