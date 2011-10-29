from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import threading
from time import sleep, time
from math import floor
import logging
import os
import rrdtool


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
            max_chunk_size = 10 * 1024 * 1024
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
        for r in self.server.reports.all():
            for s in r.sections.all():
                for v in s.variables.all():
                    rrd = RRDToolWrapper.get_rrd_path(self.server.id, s.id,
                            v.id)
                    RRDToolWrapper.create_rrd(path, v.name)
                    
                    try:
                        value = rpc.call_method(self.server.id, 'show_status',
                                {'pattern': v.name, })
                    except:
                        logger.exception("An exception ocurred when "\
                                "contacting RPC server:")
                        continue

                    if not value or v.name not in value:  # pattern not found
                        logger.debug("The pattern was not found. "\
                                "Value result: %s" % repr(value))

                    RRDToolWrapper.update(path, value[v.name])


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


class RRDToolWrapper:
    """
    TODO: add some docstring for RRDToolWrapper
    """
    @classmethod
    def get_rrd_path(cls, server_id, section_id, variable_id):
        """
        """
        return os.path.join(settings.PROJECT_ROOT, "rrd/s%ds%dv%d.rrd" %
                (server_id, section_id, variable_id))

    @classmethod
    def create_rrd(cls, path, source):
        """
        Creates the RRDTool file associated to this server-section. If it
        already exists does nothing.
        """
        if not os.path.exists(path):
            data_sources = ["DS:%s:COUNTER:60:U:U" % source]
            rrdtool.create(path, "--start", time.time(), data_sources,
                    'RRA:AVERAGE:0.5:1:24',
                    'RRA:AVERAGE:0.5:6:10'
            )

    @classmethod
    def update_rrd(cls, path, value, timestamp=None):
        """TODO: add some docstring for update_rrd"""
        rrdtool.update(path, "%s:%s" %
                (source, timestamp if timestamp else time.time()),
        )
