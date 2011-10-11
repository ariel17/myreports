#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Collector querier. Makes use of the JSON RPC server implemented in
the command 'collector_rpc' to obtain variable values from a connected MySQL
server configured previously.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from server.models import Server
from collector.models import ServerRPCClientWorker
from jsonrpclib import Server as JSONRPCClient
from lockfile import FileLock, LockTimeout
from sys import exit
import logging
from os.path import join


SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_ERROR = range(3)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--pidfile', action='store', dest='pidfile',
            default=join(settings.PROJECT_ROOT, 'collector_query.pid'),
            help='PID file for this command, to avoid multiple executions. '\
                    'Default: %s' % join(settings.PROJECT_ROOT,
                        'collector_query.pid')),
        make_option('--host', action='store', dest='host',
            default=settings.COLLECTOR_CONF['host'],
            help='Host to run query server on. Default: %s' %
            settings.COLLECTOR_CONF['host']),
        make_option('--port', action='store', dest='port',
            default=settings.COLLECTOR_CONF['port'],
            type=int, help='Port to bind the query server on. Default: %d' %
            settings.COLLECTOR_CONF['port']),
    )

    help = ""
    workers = []
    pidfile = None

    def handle(self, *args, **options):
        """
        """
<<<<<<< HEAD
        logger.info(">>> Collector RPC client started.")

        #Make pid lock file
        logger.debug("Locking PID file %s" % options['pidfile'])
        self.pidfile = FileLock(options['pidfile'])
        if self.pidfile.is_locked():
            logger.error("PID file is already locked (other process "\
                "running?).")
            exit(ALREADY_RUNNING_ERROR)
        try:
            self.pidfile.acquire(
                    timeout=settings.COLLECTOR_CONF['pidlock_timeout'])
        except LockTimeout:
            self.context.pidfile.release()
            logger.exception("Can't lock PID file:")
            logger.info(">>> Collector RPC client finished with errors.")
            exit(CONTEXT_ERROR)
        print self.pidfile.path    
=======
>>>>>>> parent of a56c501... CHG: removed ServerWorker class.

        rpc_url = "http://%s:%d" % (options['host'], options['port'])
        logger.debug("Contacting to RPC server: %s" % rpc_url)
        c = JSONRPCClient(rpc_url)

        for (id, s) in enumerate(Server.objects.filter(active=True)):
            self.workers.append(ServerRPCClientWorker(id, s, c))

        [w.start() for w in self.workers]
        [w.join() for w in self.workers]

        self.pidfile.release()
        logger.info(">>> Collector RPC client finished successful.")
