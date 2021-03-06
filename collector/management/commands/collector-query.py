#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Collector querier. Makes use of the JSON RPC server implemented in
the command 'collector_rpc' to obtain variable values from a connected MySQL
server configured previously.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


import collector.rrd as rrdtool
import logging
import os
import Queue

from collector.cache import CacheWrapper
from collector.worker import Worker
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from jsonrpclib import Server as JSONRPCClient
from lockfile import FileLock, LockTimeout
from optparse import make_option
from report.models import Section, Variable
from server.models import Server
from sys import exit


SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_EXCEPTION, RPCSERVER_ERROR = range(4)

logger = logging.getLogger(__name__)


class AlreadyRunningError(Exception):
    pass


class ContextException(Exception):
    pass


class QueryWorker(Worker):
    """
    This class wraps the Server class model with threading functionallity, to
    check the values of the variables in its reports.
    """
    rpc = None
    queue = None
    time_lapse = None
    rrd_dir = None

    def __init__(self, **kwargs):
        Worker.__init__(self, kwargs["id"])
        self.queue = kwargs["queue"]
        self.rpc = JSONRPCClient("http://%(host)s:%(port)d" % kwargs)
        self.time_lapse = kwargs["time_lapse"]
        self.rrd_dir = kwargs["rrd_dir"]

    def get_value(self, server_id, variable):
        """
        """

        if variable.query:
            f = 'doquery'
            kwargs = {'sql': variable.query, 'parsefunc': dict, }
        else:
            f = 'show_status'
            kwargs = {'pattern': variable.name, }
        logger.debug("Method: '%s', kwargs: %s" % (f, \
                repr(kwargs)))
        value = self.rpc.call_method(server_id, f, kwargs)
        logger.debug("Query result: %s" % repr(value))
        return value

    def run(self):
        while not self.queue.empty():
            try:
                (s, se, v) = self.queue.get_nowait()  # A server-variable tuple

                value = self.get_value(s.id, v)

                rrd = rrdtool.RRDWrapper.get_instance(s, se, v,
                        self.time_lapse, self.rrd_dir)
                rrd.update(value[v.name])

            except Queue.Empty:
                pass
            except Exception:
                logger.exception("Exception ocurred when processing "\
                        "an element:")
                continue

        logger.debug("Finished worker job.")


class Command(BaseCommand):
    """
    """
    help = ""
    pidfile = None

    option_list = BaseCommand.option_list + (

        make_option('--pidfile', action='store', dest='pidfile',
            default=os.path.join(settings.PROJECT_ROOT, 'collector_query.pid'),
            help='PID file for this command, to avoid multiple executions. '\
                    'Default: %s' % os.path.join(settings.PROJECT_ROOT,
                        'collector_query.pid')),

        make_option('--host', action='store', dest='host',
            default=settings.COLLECTOR_CONF['host'],
            help='Host to run query server on. Default: %s' %
            settings.COLLECTOR_CONF['host']),

        make_option('--port', action='store', dest='port',
            default=settings.COLLECTOR_CONF['port'],
            type=int, help='Port to bind the query server on. Default: %d' %
            settings.COLLECTOR_CONF['port']),

        make_option('--time-lapse', action='store', dest='time-lapse',
            default=settings.COLLECTOR_CONF['query_time-lapse'],
            type=int, help='How many seconds between update lapses. '\
                    'Default: %d' %
                    settings.COLLECTOR_CONF['query_time-lapse']),

        make_option('--rrd-dir', action='store', dest='rrd-dir',
            default=settings.RRD_DIR, help='Directory to store RRD files. '\
                    'Default: %s' % settings.RRD_DIR),

        make_option('-w', '--workers', action='store', dest='workers',
            type=int, default=settings.COLLECTOR_CONF['query_workers'],
            help="How many thread workers to use to perform request to RPC "\
                    "server. Default: %d" %
                    settings.COLLECTOR_CONF['query_workers']),
    )

    cache = CacheWrapper(cache)

    def __lock_pid(self, path):
        """
        """
        logger.debug("PID file at '%s'" % path)
        self.pidfile = FileLock(path)
        if self.pidfile.is_locked():
            raise AlreadyRunningError("PID file is already locked (other "\
                    "process running?).")
        try:
            self.pidfile.acquire(
                    timeout=settings.COLLECTOR_CONF['pidlock_timeout'])
        except LockTimeout:
            logger.exception("Can't lock PID file:")
            raise ContextException("Failed to lock pidfile.")

    def __release_pid(self):
        """
        """
        logger.debug("Releasing PID file.")
        if self.pidfile:
            self.pidfile.release()

    def __create_queue(self):
        """
        """
        queue = Queue.Queue()

        active_servers = self.cache.get_list('server_active_ids',
                'server_%d', Server, Server.objects.filter, active=True)

        for s in active_servers:

            tasks = self.cache.do().get('server_%d_tasks' % s.id, [])
            if not tasks:
                for r in s.reports.all():

                    sections = self.cache.get_list('server_%d_sections' % s.id,
                            'section_%d', Section, r.sections.all)

                    for se in sections:

                        variables = self.cache.get_list('server_%d_variables' %
                                s.id, 'variable_%d', Variable,
                                se.variables.filter, current=False)

                        [tasks.append((s, se, v)) for v in variables]
                        self.cache.do().set('server_%d_tasks' % s.id, tasks)

            [queue.put(t) for t in tasks]

        return queue

    def handle(self, *args, **options):
        """
        """
        logger.info("** Collector RPC client started. **")
        workers = []

        try:
            self.__lock_pid(options['pidfile'])

            queue = self.__create_queue()

            for id in range(options['workers']):
                workers.append(QueryWorker(id=id, queue=queue,
                    host=options['host'], port=options['port'],
                    time_lapse=options['time-lapse'],
                    rrd_dir=options['rrd-dir']))

            [w.start() for w in workers]
            [w.join() for w in workers]

            exit(SUCCESS)

        except AlreadyRunningError:
            exit(ALREADY_RUNNING_ERROR)

        except ContextException:
            exit(CONTEXT_EXCEPTION)

        finally:
            self.__release_pid()
            logger.info("** Collector RPC client finished. **")
