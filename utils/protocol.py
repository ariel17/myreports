#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description:
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import socket
import select
import logging


logger = logging.getLogger(__name__)


def new_socket():
    """
    Returns a new socket AF_INET SOCK_STREAM type.
    """
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def serve(sock, host, port, max_enqueued):
    """
    Binds the socket in the indicated host, port and maximum clients enqueued.
    """
    sock.bind((host, port))
    sock.listen(max_enqueued)
    return sock


def recv_inc(sock, length):
    """
    Incremental receiver till the indicated length.
    """
    msg = ''
    while len(msg) < length:
        chunk = sock.recv(length - len(msg))
        if chunk == '':
            return chunk
        msg = msg + chunk
    return msg


class MalformedMessageException(Exception):
    """
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


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
        self.__validate(body, server_id, method, param)
        self.server_id = server_id
        self.method = method.lower()
        self.param = param

    def __valiate(self, body=None, server_id=None, method=None, param=''):
        """
        """
        if body:
            if ':' not in body:
                raise MalformedMessageException("Body message have none "\
                        "subparts (':'): '%s'" % body)
            parts = body.split(':')
            if len(parts) < 3:  # id, method, param
                raise MalformedMessageException("Still missing some body "\
                        "part: '%s'" % body)
            server_id, method, param = parts
        try:
            server_id = int(server_id)
        except:
            raise MalformedMessageException("Parameter 'server_id' must "\
                    "be integer.")
        if server_id <= 0:
            raise MalformedMessageException("Parameter 'server_id' must"\
                    "be greater than 0.")

        for (param, name) in ((method, 'method'), (param, 'param')):
            if type(param) != str:
            raise MalformedMessageException("Parameter '%s' must be str,"\
                    " not %s" % (name, str(type(param))))

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s%s" % (str(len(self.body)).zfill(Message.HEAD_LENGTH),
                self.body)

    def get_body(self):
        return u"%d:%s:%s" % (self.server_id, self.method, self.param)

    def to_parts(self):
        """
        Returns all parts of the body splited by ':'.
        """
        return self.body.split(':')

    @classmethod
    def decode(cls, raw):
        """
        Receives a raw message and decodes into a Message object, if the raw
        content is valid.
        """
        if len(raw) < Message.HEAD_LENGTH:
            return None
        try:
            l = int(raw[:Message.HEAD_LENGTH])
        except:
            return None
        return cls(raw[Message.HEAD_LENGTH:])


class SocketBasedCommunicator(object):
    """
    Raises the bases to create server and client objects to comunicate through
    socket.
    """
    host = None
    port = None
    sock = None

    def __init__(self, host, port):
        super(SocketBasedCommunicator, self).__init__()
        self.host = host
        self.port = port
        self.sock = new_socket()

    def recv_message(self, sock):
        """
        Receives a message based in the protocol propoused in the Message
        object. Makes some validations to detect if the client was gone or if
        the integrity of the message is correct; if the message received is not
        consistent with what it says about itself it is discarded too. Returns
        a Message object if all is OK, None instead.
        """
        # handle a request from an already connected client
        body_length = recv_inc(sock, Message.HEAD_LENGTH)
        try:
            length = int(body_length)
        except ValueError:
            logger.warning("The value of body lengh received is not "\
                    "integer: %s" % repr(body_length))
            length = 0

        if length == 0:
            logger.warning("Connection was lost while receiving message "\
                    "header or there was an error on the content.")
            return None

        body = recv_inc(sock, length)
        if len(body) == 0:
            logger.warning("Connection was lost while receiving message body.")
            return None

        if len(body) != length:
            logger.warning("Body length is diferent from indicated in header."\
                    " This message will be descarted.")
            return None

        return Message(body)


class SocketServer(SocketBasedCommunicator):
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

    def __accept(self):
        """
        Accepts an incoming new client from binded socket. Also add this new
        client to input list to be monitored in reactor_cycle().
        """
        # handle a new connection
        client, address = self.sock.accept()
        logger.info("Connection %d accepted from %s." % (client.fileno(),
            address))
        self.inputs.append(client)
        return (client, address)

    def close_all(self):
        """
        Closes all sockets still handled.
        """
        [c.close() for c in self.inputs]

    def cycle_reactor(self, timeout):
        """
        It monitors for changes in all sockets handled by the application and
        does one of the next options:

        - Accepts a new incoming client and adds it to the list.
        - Receives a message from a connected client, parses it and gives an
          according response.
        - Does nothing, by timeout, by select.error or by socket.error.
        """
        try:
            ready_in, ready_out, ready_err = select.select(self.inputs, [], [],
                    timeout)
        except select.error, e:
            logger.exception("There was an error executing 'select' "\
                    "statement:")
            return None
        except socket.error, e:
            logger.exception("There was an error with socket:")
            return None

        for r in ready_in:
            logger.debug("Socket has changes: %d" % r.fileno())
            if r == self.sock:
                self.__accept()  # accepts a new client
                return None
            else:
                # handle a request from an already connected client
                message = self.recv_message(r)
                if not message:
                    r.close()
                    self.inputs.remove(r)
                    logger.info("Removed client from list.")
                    return None
                return message


class SocketClient(SocketBasedCommunicator):
    """
    A simple client implementing socket comunication.
    """

    def __init__(self, host, port):
        super(SocketClient, self).__init__(host, port)
        self.sock.connect((host, port))
        logger.info("Connected to server in %s:%d" % (host, port))
