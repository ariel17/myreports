"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from server.models import Server


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


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
