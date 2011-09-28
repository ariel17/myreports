#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Test suite for the protocol package.
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


from django.test import TestCase
from protocol.models import Message, SocketClient
from collector.models import QueryWorker
import logging


logger = logging.getLogger(__name__)


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000


class TestProtocolPackage(TestCase):
    """
    """

    def setUp(self):
        self.qw = QueryWorker(id=1, servers=[], host=SERVER_HOST,
                port=SERVER_PORT)
        self.qw.start()

    def test_message_ok(self):
        """
        """
        c = SocketClient(host=SERVER_HOST, port=SERVER_PORT)
        m = Message(server_id=1, method='show_status', param='Uptime')
        result = c.send_message(m)
        c.close()

        # checking correct message sending comparing message length against
        # bytes transmitted.
        self.assertEqual(result, len(str(m)))

        # checking correct response message format
        m = c.recv_message()


    def tearDown(self):
        self.qw.stop()
        self.qw.join()
        self.qw.sock.close_all()
