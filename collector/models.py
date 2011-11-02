from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import threading
from time import sleep, time
from math import floor
import logging
import os
import rrd as rrdtool
from django.conf import settings
from math import floor


logger = logging.getLogger(__name__)


class SimpleJSONRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """
    """
    MAX_CHUNK_SIZE = 10 * 1024 * 1024

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
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, self.MAX_CHUNK_SIZE)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)
            c_ip, c_port = self.client_address
            logger.info("Request from %s:%s [POST]: %s" % (c_ip, c_port, data))
            response = self.server._marshaled_dispatch(data)
            self.send_response(200)
            logger.info("[HTTP 200] Request accepted.")
        except Exception:
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

    def get_rrd_path(cls, server_id, section_id, variable_id):
        """
        """
        return os.path.join(settings.PROJECT_ROOT, "rrd/s%ds%dv%d.rrd" %
                (server_id, section_id, variable_id))
        

    def run(self):
        for r in self.server.reports.all():
            for s in r.sections.all():
                for v in s.variables.filter(current=False):
                    logger.debug("Contacting RPC about '%s' for %s (%s)" %
                            (v.name, self.server.name, self.server.ip))
                    rrd = rrdtool.RRD(self.get_rrd_path(self.server.id, s.id,
                        v.id))
                    rrd.create_rrd(60, ((v.name, 'COUNTER', 'U', 'U'),))
                    try:
                        if v.query:
                            f = 'doquery'
                            kwargs = {'sql': v.query, 'parsefunc': dict,}
                        else:
                            f = 'show_status'
                            kwargs = {'pattern': v.name, }
                        logger.debug("Method: '%s', kwargs: %s" %
                                (f, repr(kwargs)))
                        value = self.rpc.call_method(self.server.id, f, kwargs)
                    except:
                        logger.exception("An exception ocurred when "\
                                "contacting RPC server:")
                        continue

                    logger.debug("Query result: %s" % repr(value))
                    
                    if not value or v.name not in value:
                        continue

                    fv = int(floor(float(value[v.name])))
                    logger.debug("Floored value: %s=%d" % (v.name, fv))

                    try:
                        rrd.update(fv)
                    except rrdtool.RRDException, e:
                        logger.exception("There was an error trying to "\
                                "update RRD database:")
        logger.info("Collected stats for server %s" % self.server.name)


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
