#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Test suite for the protocol package.
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


from django.test import TestCase
from collector.models import QueryWorker
from protocol.models import RPCClient
import logging


logger = logging.getLogger(__name__)


RPC_HOST = "127.0.0.1"
RPC_PORT = 9009

print __name__


class TestRPC(TestCase):
    """
    """

    def setUp(self):
        logger.info("Setting up RPC Server at http://%s:%d" % (RPC_HOST,
            RPC_PORT))
        self.qw = QueryWorker(id=1, servers=[], host=RPC_HOST,
                port=RPC_PORT)
        self.qw.start()

    def test_message_ok(self):
        """
        """
        c = RPCClient(host=RPC_HOST, port=RPC_PORT)
        result = c.show_status(1, 'uptime')

    def tearDown(self):
        self.qw.stop()
        self.qw.join()
