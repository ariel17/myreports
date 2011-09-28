#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description:
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import jsonrpclib
import logging


logger = logging.getLogger(__name__)


class JSONRPCHandler(object):
    """
    """
    def __init__(self, servers):
        super(JSONRPCHandler, self).__init__()
        self.servers = servers

    def handle(self, **kwargs):
        """
        """
        pass
