#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Test suite for the protocol package.
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


from django.test import TestCase
from server.models import Server
from models import RPCHandler


class TestRPCHandler(TestCase):
    """
    """

    def setUp(self):
        self.s = Server(ip="127.0.0.1", username="root", name="localhost_test")
        self.s.save()
        self.s.connect()

    def tearDown(self):
        self.s.close()

    def test_call_method(self):
        """
        Test remote call to a Server method.
        """
        self.rh = RPCHandler([self.s,])
        r = self.rh.call_method(self.s.id, "show_processlist")
        self.assertTrue(len(r))
