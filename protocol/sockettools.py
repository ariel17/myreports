#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: 
"""
__author__ = "Ariel Gerardo Ríos (arielgerardorios@gmail.com)"


import socket
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


def send_inc(sock, message, length=None):
    """
    """
    if not length:
        length = len(message)
    sended = 0
    while sended < length:
        sended += sock.send(message[sended:])
    return sended
