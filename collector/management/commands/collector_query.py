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
from sys import exit
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
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

    def handle(self, *args, **options):
        """
        """

        rpc_url = "http://%s:%d" % (options['host'], options['port'])
        logger.debug("Contacting to RPC server: %s" % rpc_url)
        c = JSONRPCClient(rpc_url)

        for (id, s) in enumerate(Server.objects.filter(active=True)):
            self.workers.append(ServerRPCClientWorker(id, s, c))

        [w.start() for w in self.workers]
        [w.join() for w in self.workers]
