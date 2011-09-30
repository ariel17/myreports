#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Test suite for the protocol package.
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


from django.test import TestCase
from server.models import Server
from models import QueryWorker
from jsonrpclib import Server as JSONRPCClient
import logging


logger = logging.getLogger(__name__)


RPC_HOST = "127.0.0.1"
RPC_PORT = 9009


class TestRPC(TestCase):
    """
    """

    def setUp(self):
        logger.info("Setting up RPC Server at http://%s:%d" % (RPC_HOST,
            RPC_PORT))
        self.servers = Server.objects.all()
        [s.connect() for s in self.servers]
        self.qw = QueryWorker(id=1, servers=self.servers, host=RPC_HOST,
                port=RPC_PORT)
        self.qw.start()

    def test_message_ok(self):
        """
        """
        pattern = 'Uptime'
        c = JSONRPCClient("http://%s:%d" % (RPC_HOST, RPC_PORT))
        result = c.call_method(1, 'show_status', {'pattern': pattern})
        d = dict(result)
        self.assertTrue(pattern in d)


    def tearDown(self):
        self.qw.stop()
        self.qw.join()
        [s.close() for s in self.servers]
