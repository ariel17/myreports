#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Test suite for the Django application 'collector'.
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
        self.rh = RPCHandler([self.s, ])
        r = self.rh.call_method(self.s.id, "show_processlist")
        self.assertTrue(len(r))


class TestRRD(TestCase):
    """
    TODO: define tests to do.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestRRDWrapper(TestCase):
    """
    TODO: define tests to do.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestCollectorGraphCommand(TestCase):
    """
    TODO: define tests to do.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestCollectorRPCCommand(TestCase):   
    """
    TODO: define tests to do.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestCollectorQueryCommand(TestCase):       
    """
    TODO: define tests to do.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass
