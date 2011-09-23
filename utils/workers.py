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


class ServerWorker(Worker):
    """
    This class wraps the Server class model with threading functionallity.
    """

    server = None

    def __init__(self, id, server):
        super(ServerWorker, self).__init__(id)
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


class SocketWorker(Worker):
    """
    This is a theaded socket server to handle external request for making
    queries.
    """

    host = None
    port = None
    sock = None
    servers = None

    def __init__(self, id, servers, host, port):
        super(SocketWorker, self).__init__(id)
        self.host = host
        self.port = port
        self.servers = servers
        logger.info("Handling request in %s:%d" % (host, port))

    def __serve(self):
        """
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(settings.COLLECTOR_MAX_WAITING)                 

    def __recv(self, sock, length):
        """
        """
        msg = ''
        while len(msg) < length:
            chunk = sock.recv(length-len(msg))
            if chunk == '':
                logger.warning("Connection was broken wen receiving message.")
                return chunk
            msg = msg + chunk
        logger.debug("Raw message received: '%s' (%d)" % (msg, len(msg)))
        return msg

    def __accept(self, sock, inputs=None):
        """
        """
        # handle a new connection
        client, address = sock.accept()
        logger.info("Connection %d accepted from %s." % (client.fileno(),
            address))
        if inputs:
            inputs.append(client)
        return (client, address)

    def __do_query(self, server_id, method, param):
        """
        """
        for s in self.servers:
            if s.id == server_id:
                return getattr(s, method)(param)

    def __recv_message(self, sock):
        # handle a request from an already connected client
        body_length = self.__recv(sock, Message.HEAD_LENGTH)
        try:
            length = int(body_length)
        except ValueError:
            logger.warning("The value of body lengh received "\
                    "is not integer: %s" % repr(body_length))
            length = 0
                                                                    
        if length == 0:
            logger.warning("Connection was lost while receiving message "\
                    "header.")
            return None
                                                                    
        body = self.__recv(sock, length)

        if len(body) == 0:
            logger.warning("Connection was lost while receiving message body.")
            return None

        if len(body) <> length:
            logger.warning("Body length is diferent from indicated in header."\
                    " This message will be descarted.")
            return None
        
        return Message(body)

    def run(self):
        self.__serve()
        logger.debug("Now the socket is listening.")
        inputs = [self.sock, ]

        logger.debug("Starting the reactor.")
        while self.running:
            try:
                ready_in, ready_out, ready_err = select.select(inputs, [], [],
                        settings.COLLECTOR_REACTOR_TIME)
            except select.error, e:
                logger.exception("There was an error executing 'select' "\
                        "statement:")
            except socket.error, e:
                logger.exception("There was an error with socket:")

            for r in ready_in:
                logger.debug("Socket has changes: %d" % r.fileno())
                if r == self.sock:
                    self.__accept(self.sock, inputs)  # accepts a new client
                else:
                    # handle a request from an already connected client
                    message = self.__recv_message(r)
                    if not message:
                        r.close()
                        inputs.remove(r)
                        logger.info("Removed client from list.")
                        continue
                    server_id, method, param = message.to_parts()
                    result = self.__do_query(int(server_id), method, param)
                    message = Message(repr(result))
                    r.send("%s" % str(message))
            
        # time to go: closing all input sockets still open
        for i in inputs:
            i.close()
