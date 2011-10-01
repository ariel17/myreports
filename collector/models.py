from history.models import SnapshotFactory
import threading
from time import sleep, time
from math import floor
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
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


class ServerWorker(Worker):
    """
    This class wraps the Server class model with threading functionallity.
    """

    server = None

    def __init__(self, id, server):
        super(ServerWorker, self).__init__(id)
        self.server = server
        logger.info("Handling server %s" % server)

    def run(self):
        try:
            logger.debug("Connecting to server.")
            self.server.connect()

            # this is the minimal time period between checks (heartbeat)
            min_period, max_period = self.server.get_periods()
            logger.debug("Heartbeat period: %d seconds." % min_period)

            variables = self.server.get_variables()
            logger.debug("Variables to check: %s" % variables)

            base_time = time()
            while self.running:
                logger.debug("Sleeping %d seconds." % min_period)
                sleep(min_period)

                # getting actual seconds passed since thread start as int
                t = int(floor(time() - base_time))

                # check values for all variables of all reports assigned.
                for (period, v) in variables:
                    # only numeric status variables or 'custom' type variables
                    # and numeric periods (period == None or period == 0 means
                    # check only current values).
                    if v.data_type not in 'na' or not period:
                        continue

                    # if t matchs a time check period of this variable, then
                    # do a snapshot.
                    if t % period == 0:
                        s = SnapshotFactory.take_snapshot(self.server,
                                variable=v)
                        logger.debug("Taked snapshot: %s" % s)

                # if t has reached max_period (time when all variables has
                # been checked at least once), then base_time moves into
                # now.
                if t >= max_period:
                    base_time = time()
                    logger.debug("Reseted base time to now.")

        except Exception:
            logger.exception("Error occoured when contacting server:")
        finally:
            logger.info("Finishing thread.")

    def stop(self):
        Worker.stop(self)
        if self.server:
            self.server.close()


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
        s = self.servers[id]
        return getattr(s, method)(**kwargs)


class QueryWorker(Worker):
    """
    This is a worker to handle query request to do on a configured MySQL server
    through JSON RPC protocol.
    """
    rpc = None

    def __init__(self, id, servers, host, port):
        super(QueryWorker, self).__init__(id)
        self.rpc = SimpleJSONRPCServer((host, port))
        self.rpc.register_instance(RPCHandler(servers))

    def stop(self):
        Worker.stop(self)
        try:
            self.rpc.shutdown()
        except:
            pass

    def run(self):
        self.rpc.serve_forever()
