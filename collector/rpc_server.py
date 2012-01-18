#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: JSON RPC Server implementation.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


import os
import logging
from django.conf import settings
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer


logger = logging.getLogger(__name__)


class SimpleJSONRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """
    JSON implementation for RPC protocol.
    """
    MAX_CHUNK_SIZE = 10 * 1024 * 1024

    def do_GET(self):
        """
        HTTP GET method processor.
        """
        c_ip, c_port = self.client_address
        logger.info("[Request] Client %s:%s method GET: %s" %
                (c_ip, c_port, data))
        logger.warning("[Response] HTTP 400 - Method not allowed.")
        self.send_response(400)
        response = ''
        self.send_header("Content-type", "application/json-rpc")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)

    def do_POST(self):
        """
        HTTP POST method processor.
        """
        if not self.is_rpc_path_valid():
            logger.warning("[Response] HTTP 404 - The path requested "\
                    "is not a valid address.")
            self.report_404()
            return

        try:
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, self.MAX_CHUNK_SIZE)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)
            c_ip, c_port = self.client_address
            logger.info("[Request] Client %s:%s method POST: %s" %
                    (c_ip, c_port, data))
            response = self.server._marshaled_dispatch(data)
            status = 200
            message = "Request accepted."
        except Exception:
            logger.exception("Exception processing request:")
            status = 500
            message = "Internal Server Error."
            err_lines = traceback.format_exc().splitlines()
            trace_string = '%s | %s' % (err_lines[-3], err_lines[-1])
            fault = jsonrpclib.Fault(-32603, 'Server error: %s' % trace_string)
            response = fault.response()
        finally:
            logger.info("[Response] HTTP %d - %s" % (status, message))
            self.send_response(status)

        logger.info("[Response] Content: %s" % repr(response))
        self.send_header("Content-type", "application/json-rpc")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)


class RPCHandler:
    """
    This class is the RPC backend that knows what to do with a correct request
    to this service.
    """
    servers = {}

    def __init__(self, servers):
        self.__servers_to_dict(servers)

    def __servers_to_dict(self, server_list):
        """
        Receives a list of Server objects and returns a dict with the same
        objects indexed by id.
        """
        for s in server_list:
            self.servers[s.id] = s

    def call_method(self, id, method, kwargs={}):
        """
        Performs a call to the indicated method with kwargs given to a Server
        object with the same `id` value as the idoneous parameter.
        """
        s = self.servers.get(id, None)
        return getattr(s, method)(**kwargs) if s else None


class StoppableSimpleJSONRPCServer(SimpleJSONRPCServer):
    """
    """
    pass
