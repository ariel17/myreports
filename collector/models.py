from history.models import SnapshotFactory
import threading
from time import sleep, time
from math import floor
import logging


logger = logging.getLogger(__name__)


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
