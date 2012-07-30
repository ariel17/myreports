#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: TODO
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.test import TestCase
from server.models import Server


class ServerTest(TestCase):
    """
    Testing for Server model.
    """

    def setUp(self):
        self.s = Server(ip="127.0.0.1", username="root", name="localhost_test")
        self.s.save()

    def teatDown(self):
        """
        """
        self.s.close()

    def test_connect(self):
        """
        Testing 'connection' method for Server class.
        """
        self.s.close()
        self.assertIn(self.s.connect(), [True, False])

    def test_doquery(self):
        """
        Testing query request and result format.
        """
        self.s.restart()

        sql = "SELECT NOW();"
        r = self.s.doquery(sql)
        self.assertTrue(r)

    def test_show_status(self):
        """
        Testing status query for server.
        """
        self.s.restart()
        r = self.s.show_status(pattern='Threads_running')
        self.assertTrue(r)
