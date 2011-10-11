from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from history.models import SnapshotFactory
import threading
from time import sleep, time
from math import floor
import logging


logger = logging.getLogger(__name__)


class SimpleJSONRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """
    """

    def do_GET(self):
        """
        """
        c_ip, c_port = self.client_address
        logger.info("Request from %s:%s [GET]: %s" % (c_ip, c_port, data))
        logger.warning("[HTTP 400] Method not allowed.")
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
        """
        if not self.is_rpc_path_valid():
            logger.warning("[HTTP 404] The path requested is not a valid "\
                    "address.")
            self.report_404()
            return
        try:
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)
            c_ip, c_port = self.client_address
            logger.info("Request from %s:%s [POST]: %s" % (c_ip, c_port, data))
            response = self.server._marshaled_dispatch(data)
            self.send_response(200)
            logger.info("[HTTP 200] Request accepted.")
        except Exception, e:
            logger.exception("[HTTP 500] Internal Server Error:")
            self.send_response(500)
            err_lines = traceback.format_exc().splitlines()
            trace_string = '%s | %s' % (err_lines[-3], err_lines[-1])
            fault = jsonrpclib.Fault(-32603, 'Server error: %s' % trace_string)
            response = fault.response()
        if response == None:
            response = ''
        logger.info("Response: %s" % response)
        self.send_header("Content-type", "application/json-rpc")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)


class Worker(threading.Thread):
    """
    This is a generic threaded worker.
    """

    server = None
    running = True

    def __init__(self, id):
        super(Worker, self).__init__(name="Worker#%d" % id)
        logger.info("Initialized thread with name '%s'" % self.name)

    def stop(self):
        """
        Sets the flag 'running' to False. This breaks the thread loop.
        """
        self.running = False

    def run(self):
        raise NotImplementedError("Must implement this method.")


class ServerRPCClientWorker(Worker):
    """
    This class wraps the Server class model with threading functionallity, to
    check the values of the variables in its reports.
    """
    server = None
    rpc = None

    def __init__(self, id, server, rpc):
        super(ServerRPCClientWorker, self).__init__(id)
        self.server = server
        self.rpc = rpc

    def run(self):
        try:
            logger.info("Collecting info for server %s" % self.server)
            variables = self.server.get_variables()
            logger.debug("Variables to check: %s" % variables)

            # check values for all variables of all reports assigned.
            for (period, current, v) in variables:
                # only numeric status variables or 'custom' type variables
                # and not variables conforming sections for current values
                # (current == True).
                if v.data_type not in 'na' or current:
                    continue

                s = SnapshotFactory.take_snapshot(self.server, self.rpc,
                        variable=v)
                logger.info("Taked snapshot: %s" % s)

        except Exception:
            logger.exception("Error occoured when contacting RPC server:")
        finally:
            logger.info("Collect done.")


class RPCHandler(object):
    """
    """
    servers = {}

    def __init__(self, servers):
        super(RPCHandler, self).__init__()
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
        """
        s = self.servers.get(id, None)
        return getattr(s, method)(**kwargs) if s else None
