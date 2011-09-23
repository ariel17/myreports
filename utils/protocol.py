#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import socket

def new_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def serve(self, sock, host, port, max_enqueued=1):
    """
    """
    sock.bind((self.host, self.port))
    sock.listen(max_enqueued)                 
    return sock


def recv_inc(self, sock, length):
    """
    """
    msg = ''
    while len(msg) < length:
        chunk = sock.recv(length-len(msg))
        if chunk == '':
            return chunk
        msg = msg + chunk
    return msg


class Message(object):
    """
    This is a message to use for comunication between Collector server and
    clients. Has the following components:

    [XXX] head: Integer zero-filled to left, 3 digits.
    [XXXXXXXX...] body: String with length as indicated in 'length' field.

    Also the body is separated in 3 parts that will be verificated as a valid
    message:

        <server_id>:<method>:<params>

    Example:

    0201:show_status:Uptime
     | |      |         |______> 'Uptime': The variable to check.
     | |      |______> 'show_status': The method to execute.
     | |______> '1': The server Id to use.
     |______> '020': The length of entire body.

    """
    HEAD_LENGTH = 3  # chars

    def __init__(self, body=None, server_id=None, method=None, param=''):
        super(Message, self).__init__()
        if body:
            self.body = body
        else:
            self.body = "%d:%s:%s" % (server_id, method, param)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s%s" % (str(len(self.body)).zfill(Message.HEAD_LENGTH),
                self.body)

    def to_parts(self):
        return self.body.split(':')

    @classmethod
    def decode(cls, raw):
        if len(raw) < Message.HEAD_LENGTH:
            return None
        try:
            l = int(raw[:Message.HEAD_LENGTH])
        except:
            return None
        return cls(raw[Message.HEAD_LENGTH:])


class SocketBased(object):
    """
    """
    host = None
    port = None
    sock = None

    def __init__(self, host, port):
        super(SocketBased, self).__init__()
        self.host = host
        self.port = port
        self.sock = new_socket()

    def recv_message(self, sock):
        """
        """
        # handle a request from an already connected client
        body_length = recv_inc(sock, Message.HEAD_LENGTH)
        try:
            length = int(body_length)
        except ValueError:
            logger.warning("The value of body lengh received "\
                    "is not integer: %s" % repr(body_length))
            length = 0

        if length == 0:
            logger.warning("Connection was lost while receiving message "\
                    "header.")
            return None

        body = recv_inc(sock, length)
        if len(body) == 0:
            logger.warning("Connection was lost while receiving message body.")
            return None

        if len(body) <> length:
            logger.warning("Body length is diferent from indicated in header."\
                    " This message will be descarted.")
            return None
        
        return Message(body)


class SocketServer(SocketBased):
    """
    This is a theaded socket server to handle external request for making
    queries.
    """
    inputs = []

    def __init__(self, host, port, max_enqueued=1):
        super(SocketServer, self).__init__(host, port)
        serve(self.sock, host, port, max_enqueued)
        logger.info("Handling request in %s:%d" % (host, port))
        self.inputs.append(self.sock)

    def accept(self, sock):
        """
        """
        # handle a new connection
        client, address = sock.accept()
        logger.info("Connection %d accepted from %s." % (client.fileno(),
            address))
        self.inputs.append(client)
        return (client, address)

    def close_all(self):
        """
        """
        [c.close() for c in self.inputs]


class SocketClient(SocketBased):
    """
    Collector daemon socket client handler.
    """

    def __init__(self, host, port):
        super(SocketClient, self).__init__(host, port)
        self.sock.connect((host, port))
