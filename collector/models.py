from time import sleep, time
from math import floor
import logging
import os
import threading
from math import floor

from django.conf import settings

from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import rrd as rrdtool


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

    def get_path(cls, server_id, variable_id, sufix='.rrd'):
        """
        """
        return os.path.join(settings.RRD_DIR, "s%dv%d%s" % (server_id,
            variable_id, sufix))
    
    def set_last_update(self, path, timestamp):
        """TODO: add some docstring for set_last_update"""
        with open(path, 'w') as f:
            f.write(str(timestamp).strip())
    
    def get_last_update(self, path):
        """
        """
        with open(path, 'r') as f:
            return int(f.readline().strip())

    def must_update(self, last_update, now):
        """TODO: add some docstring for must_update"""
        diff = now - last_update
        if diff < settings.CRONTAB_TIME_LAPSE:
            return (False, diff)
        return (True, diff)

    def fix_update_time(self, last_update, now):
        """TODO: add some docstring for fix_update_time"""
        factor = int(floor((now - last_update) / settings.CRONTAB_TIME_LAPSE))
        return factor * settings.CRONTAB_TIME_LAPSE + last_update

    def run(self):
        now = int(time())
        logger.debug("Real time=%d" % now)
        for r in self.server.reports.all():
            for s in r.sections.all():
                for v in s.variables.filter(current=False):
                    rrd_path = self.get_path(self.server.id, v.id)
                    last_update_path = self.get_path(self.server.id, v.id,
                            '.last-update')
                    rrd = rrdtool.RRD(rrd_path)

                    if not os.path.exists(rrd_path):
                        now_start = now - settings.CRONTAB_TIME_LAPSE
                        logger.info("Creating new RRD file in %s" % rrd_path)
                        try:
                            rrd.create_rrd(
                                    settings.CRONTAB_TIME_LAPSE,
                                    ((v.name, 'GAUGE', 'U', 'U'),),
                                    start=now_start)
                        except rrdtool.RRDException:
                            logger.exception("An exception ocurred when "\
                                    "creating RRD database:")
                            continue
                        self.set_last_update(last_update_path, now_start)
                        logger.debug("Setted initial time to %d" % now_start)

                    last_update = self.get_last_update(last_update_path)    
                    must_update, sec = self.must_update(last_update, now)
                    if not must_update:
                        logger.warn("It isn't time to update: %d seconds "\
                                "(must at >=%d seconds)." % (sec, \
                                settings.CRONTAB_TIME_LAPSE))
                        continue

                    logger.debug("It is time to update :) %d seconds "\
                            "(must at >=%d seconds)." % (sec, \
                            settings.CRONTAB_TIME_LAPSE))

                    logger.debug("Contacting RPC about '%s' for %s (%s)" %
                            (v.name, self.server.name, self.server.ip))

                    if v.query:
                        f = 'doquery'
                        kwargs = {'sql': v.query, 'parsefunc': dict, }
                    else:
                        f = 'show_status'
                        kwargs = {'pattern': v.name, }
                    logger.debug("Method: '%s', kwargs: %s" % (f, \
                            repr(kwargs)))

                    try:
                        value = self.rpc.call_method(self.server.id, f, kwargs)
                    except:
                        logger.exception("An exception ocurred when "\
                                "contacting RPC server:")
                        continue

                    logger.debug("Query result: %s" % repr(value))

                    if not value or v.name not in value:
                        logger.warn("Missing required value.")
                        continue

                    fv = int(floor(float(value[v.name])))
                    logger.debug("Floored value: %s=%d" % (v.name, fv))

                    fixed_time = self.fix_update_time(last_update, now)
                    logger.debug("Fixed time=%d" % fixed_time)

                    try:
                        rrd.update((fixed_time, fv),)
                    except rrdtool.RRDException, e:
                        logger.exception("There was an error trying to "\
                                "update RRD database:")

                    self.set_last_update(last_update_path, fixed_time)
                    logger.debug("Updated time to %d in %s" %
                            (fixed_time, last_update_path),)
            
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
