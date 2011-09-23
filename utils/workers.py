from django.conf import settings
from server.models import Server
from history.models import VariableSnapshot, UsageSnapshot, SnapshotFactory
import threading
from time import sleep, time
import logging
from math import floor
from protocol import Message
import socket
import select

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


class ServerWorker(threading.Thread):
    """
    This class wraps the Server class model with threading functionallity.
    """

    server = None

    def __init__(self, id, server):
        super(Worker, self).__init__(id)
        self.server = server
        logger.info("Handling server %s" % server)

    def restart(self):
        self.server.restart()

    def run(self):
        logger.debug("Core initialized.")
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
                        s = SnapshotFactory.take_snapshot(self.server, variable=v)
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

    def __del__(self):
        if self.server:
            self.server.close()


class SocketWorker(object):
    """
    This is a theaded socket server to handle external request for making
    queries.
    """

    host = None
    port = None
    sock = None
    servers = None

    def __init__(self, id, servers, host="0.0.0.0", port=9000):
        super(SocketWorker, self).__init__(id)
        self.host = host
        self.port = port
        self.servers = servers
        logger.info("Handling request in %s:%d" % (host, port))

    def __serve(self):
        """
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)  # Non-blocking socket
        self.sock.bind((self.host, self.port))
        self.sock.listen(settings.COLLECTOR_MAX_WAITING)                 

    def __recv(self, sock, length):
        """
        """
        msg = ''
        while len(msg) < length:
            chunk = sock.recv(length-len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        logger.debug("Raw message received: '%s' (%d)" % (msg, len(msg)))
        return msg

    def __do_query(self, server_id, method, param):
        """
        """
        for s in self.servers:
            if s.id == server_id:
                return getattr(s, method)(param)

    def run(self):
        self.__serve()
        inputs = [self.sock, ]

        while self.running:
            try:
                ready_in, ready_out, ready_err = select.select(inputs, [], [])
            except select.error, e:
                logger.exception("There was an error executing 'select' "\
                        "statement:")
            except socket.error, e:
                logger.exception("There was an error with socket:")

            for r in ready_in:
                if r == s:
                   # handle a new connection
                    client, address = s.accept()
                    logger.info("Connection %d accepted from %s." %
                            (client.fileno(), address))
                    inputs.append(client)
                else:
                    # handle a request from an already connected client
                    try:
                        body_length = self.__recv(r, self.HEAD_LENGTH)
                    except ValueError:
                        logger.exception("The value of body lengh received "\
                                "is not integer:")
                        continue
                    if len(body_length) == 0:
                        inputs.remove(r)
                        continue
                    message = Message(self.__recv(body_length))
                    method, param = message.to_parts()
                    response = Message(str(self.__do_query(method, param)))
                    r.send(str(response))
            
            # time to go: closing all input sockets still open
            for i in inputs:
                i.close()
