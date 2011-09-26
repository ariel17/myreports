#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: A socket client to use with Collector daemon. It can be used as an
extension of models to reuse the existent connection handled by Collector
daemon instead of creating a new one to obtain data about variables or usage,
in the name of less overhead. :)
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import socket
from protocol import Message, SocketClient


class CollectorHandler(SocketClient):
    """
    Collector daemon socket client handler.
    """

    def __init__(self, host, port):
        super(CollectorHandler, self).__init__(host, port)

    def __unicode__(self):
        return u"<CollectorHandler host='%s', port=%d>" % (self.host,
                self.port)

    def close(self):
        """
        Closes the current connection with Collector daemon.
        """
        if sock:
            self.sock.close()
    
    def get(self, server_id, method, param):
        message = Message(server_id, method, param)
        self.sock.send(str(message))
        message = self.recv_message(self.sock)
        # TODO: parse to a "human-redable" content?
        return message
        
