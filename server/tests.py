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
        s = Server(ip="127.0.0.1", username="root", name="localhost_test")
        s.save()

    def test_connection(self):
        self.assertEqual(True, True)
    
