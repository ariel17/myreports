#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Collector querier. Makes use of the JSON RPC server implemented in
the command 'collector_rpc' to obtain variable values from a connected MySQL
server configured previously.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from sys import exit
from math import floor
from time import time
import os
import logging
from os.path import join
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Server
from collector.models import Worker

from jsonrpclib import Server as JSONRPCClient
from lockfile import FileLock, LockTimeout

import collector.rrd as rrdtool


SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_ERROR, RPCSERVER_ERROR = range(4)

logger = logging.getLogger(__name__)


class RPCClientWorker(Worker):
    """
    This class wraps the Server class model with threading functionallity, to
    check the values of the variables in its reports.
    """
    server = None
    rpc = None

    def __init__(self, id, server, rpc):
        super(RPCClientWorker, self).__init__(id)
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
        """
        Changes the timestamp to use as time mark for update. Since it doesn't
        now how many time had passed (maybe the server was down for a few hours
        or not) must determine the closer timestamp passed.

        Parameteres:
        @last_update (int): last timestamp saved.
        @now (int): actual timestamp obteined.

        Returns:
        Int: The closer timestamp mark to update.
        """
        factor = (now - last_update) / settings.CRONTAB_TIME_LAPSE
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
                        now_start -= now_start % 10  # fixed to fit rrd laps
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
                self.workers.append(RPCClientWorker(id, s, c))

            [w.start() for w in self.workers]
            [w.join() for w in self.workers]

            logger.info("** Collector RPC client finished. **")

        finally:
            self.pidfile.release()
