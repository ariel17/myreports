#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Collector querier. Makes use of the JSON RPC server implemented in
the command 'collector_rpc' to obtain variable values from a connected MySQL
server configured previously.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from sys import exit
import logging
from os.path import join
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Server
from collector.models import ServerRPCClientWorker

from jsonrpclib import Server as JSONRPCClient
from lockfile import FileLock, LockTimeout


SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_ERROR, RPCSERVER_ERROR = range(4)

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
        logger.info("** Collector RPC client started. **")

        #Make pid lock file
        logger.debug("Locking PID file %s" % options['pidfile'])
        self.pidfile = FileLock(options['pidfile'])
        if self.pidfile.is_locked():
            logger.error("PID file is already locked (other process "\
                "running?).")
            logger.error("** Collector RPC client finished with errors. **")
            exit(ALREADY_RUNNING_ERROR)
        try:
            try:
                self.pidfile.acquire(
                        timeout=settings.COLLECTOR_CONF['pidlock_timeout'])
            except LockTimeout:
                logger.exception("Can't lock PID file:")
                logger.error("** Collector RPC client finished with errors. **")
                exit(CONTEXT_ERROR)

            rpc_url = "http://%s:%d" % (options['host'], options['port'])
            logger.debug("RPC server in %s" % rpc_url)
            try:
                c = JSONRPCClient(rpc_url)
            except Exception:
                logger.exception("Exception occurred when trying to contact "\
                        "RPC server:")
                logger.error("** Collector RPC client finished with errors. **")
                exit(RPCSERVER_ERROR)
                
            for (id, s) in enumerate(Server.objects.filter(active=True)):
                self.workers.append(ServerRPCClientWorker(id, s, c))

            [w.start() for w in self.workers]
            [w.join() for w in self.workers]

            logger.info("** Collector RPC client finished. **")

        finally:
            self.pidfile.release()
