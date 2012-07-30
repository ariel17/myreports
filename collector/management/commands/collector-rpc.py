"""
Copyright (c) 2009, Sean Creeley
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
  * Neither the name of the Optaros, Inc. nor the names of its contributors may
      be used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=============
DaemonCommand
=============

Django Management Command for starting a daemon.

Use
===

Simple use of daemon command::

    from daemonextension import DaemonCommand
    from django.conf import settings
    import os

    class Command(DaemonCommand):

        stdout = os.path.join(settings.DIRNAME, "log/cubbyscott.out")
        stderr = os.path.join(settings.DIRNAME, "log/cubbyscott.err")
        pidfile = os.path.join(settings.DIRNAME, "pid/cb_link.pid")

        def handle_daemon(self, *args, **options):
            from flopsy import Connection, Consumer
            consumer = Consumer(connection=Connection())
            consumer.declare(queue='links',
                             exchange='cubbyscott',
                             routing_key='importer', auto_delete=False)

            def message_callback(message):
                print 'Recieved: ' + message.body
                consumer.channel.basic_ack(message.delivery_tag)

            consumer.register(message_callback)

            consumer.wait()

call::

    python manage.py linkconsumer

"""

import daemon
import logging
import signal

from collector.cache import CacheWrapper
from collector.rpc_server import StoppableSimpleJSONRPCServer, \
        SimpleJSONRPCRequestHandler, RPCHandler
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from lockfile import FileLock, LockTimeout
from optparse import make_option
from server.models import Server
from sys import exit


logger = logging.getLogger(__name__)

SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_ERROR = range(3)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--chroot_directory', action='store', default=None,
            dest='chroot_directory', help='Full path to a directory to set '\
                    'as the effective root directory of the process.'),
        make_option('--working_directory', action='store',
            dest='working_directory', default="/", help='Full path of the '\
                    'working directory to which the process should change '\
                    'on daemon start.'),
        make_option('--umask', action='store', dest='umask', default=0,
            type="int", help='File access creation mask ("umask") to set '\
                    'for the process on daemon start.'),
        make_option('--pidfile', action='store', dest='pidfile', default=None,
            help='Context manager for a PID lock file. When the daemon '\
                    'context opens and closes, it enters and exits the '\
                    '`pidfile` context manager.'),
        make_option('--detach_process', action='store', default=True,
            dest='detach_process', help='If ``True``, detach the process '\
                    'context when opening the daemon context; if ``False``, '\
                    'do not detach.'),
        make_option('--uid', action='store', dest='uid', help='The user ID '\
                '("UID") value to switch the process to on daemon start.',
                default=None),
        make_option('--gid', action='store', dest='gid', help='The group ID '\
                '("GID") value to switch the process to on daemon start.',
                default=None),
        make_option('--prevent_core', action='store', dest='prevent_core',
            default=True, help='If true, prevents the generation of core '\
                    'files, in order to avoid leaking sensitive information '\
                    'from daemons run as `root`.'),
        make_option('--stdin', action='store', dest='stdin', default=None,
            help='Standard In'),
        make_option('--stdout', action='store', dest='stdout', default=None,
            help='Standard Out'),
        make_option('--stderr', action='store', dest='stderr', default=None,
            help='Standard Error'),
        make_option('--host', action='store', dest='host',
            default=settings.COLLECTOR_CONF['host'],
            help='Host to run query server on. Default: %s' %
            settings.COLLECTOR_CONF['host']),
        make_option('--port', action='store', dest='port',
            default=settings.COLLECTOR_CONF['port'],
            type=int, help='Port to bind the query server on. Default: %d' %
            settings.COLLECTOR_CONF['port']),
    )
    help = "Starts the Collector RPC daemon and fetch status of all MySQL "\
            "servers configured.\n\n"\
            "Example:\n\n"\
            "$ python manage.py collector_rpc "\
            "--stdout=/var/log/collector-out.log "\
            "--stderr=/var/log/collector-err.log "\
            "--pidfile=/var/run/collector.pid --host 127.0.0.1 --port 8001"

    rpc = None
    servers = []
    context = daemon.DaemonContext()
    cache = CacheWrapper(cache)

    def tear_down(self, signum=None, frame=None):
        """
        Handle to all task that must be made to close clean and fast.
        """
        if signum and frame:
            logger.debug(">> Signal received: signum=%s frame=%s" %
                    (repr(signum), repr(frame)))
        logger.info(">> Tearing down.")
        self.__close_servers()
        self.__stop_rpc()
        self.__close_streams()
        logger.info("Closing context.")
        # self.context.pidfile.release()
        self.context.close()

    def reload_config(self, signum, frame):
        """
        Reloads configuration and reconnects for all servers.
        """
        logger.info(">>> Reloading configuration.")
        logger.debug("Restarting all connections.")
        self.__close_servers()
        self.__connect_servers()

    def __connect_servers(self):
        """
        Connects to all enabled MySQL servers in the model Server and stores
        them in a list.
        """
        logger.info("Connecting to servers.")

        active_servers = self.cache.get_list('server_active_ids',
                'server_%d', Server, Server.objects.filter, active=True)
        self.servers = [s for s in active_servers if s.connect()]
        logger.debug(repr(self.servers))
        return self.servers

    def __close_servers(self):
        """
        Closes all existent connections to MySQL servers.
        """
        logger.info("Closing all server connections.")
        [s.close() for s in self.servers]
        self.servers = []

    def __start_rpc(self):
        """
        Starts the JSON RPC server binded in host and port indicated by
        parameter.
        """
        logger.info("Starting JSON RPC server: %s %d" % (self.host, self.port))
        self.rpc = StoppableSimpleJSONRPCServer((self.host, self.port),
                requestHandler=SimpleJSONRPCRequestHandler)
        self.rpc.register_instance(RPCHandler(self.__connect_servers()))
        self.rpc.serve_forever()

    def __stop_rpc(self):
        """
        Stops the JSON RPC server priviously started.
        """
        logger.info("Stopping JSON RPC server.")
        if self.rpc:
            self.rpc.shutdown()

    def __close_streams(self):
        """
        Closes opened standard steams.
        """
        logger.info("Closing opened streams.")
        for s in (self.context.stdin, self.context.stdout,
                self.context.stderr):
            try:
                s.close()
            except:
                pass

    def handle(self, *args, **options):
        """
        Takes the options and starts a daemon context from them.

        Example::

            python manage.py linkconsumer --pidfile=/var/run/cb_link.pid
                --stdout=/var/log/cb/links.out --stderr=/var/log/cb/links.err

        """
        # Making basic checks for some parameters

        # Checking required parameters
        for param in ['stdout', 'stderr', 'pidfile']:
            if not options.get(param, None):
                logger.error("Invalid value for parameter '%s'. Use -h to "\
                        "read help." % param)
                exit(CONTEXT_ERROR)

        self.host = options['host']
        self.port = options['port']

        # Openning streams
        if options['stdin']:
            try:
                self.context.stdin = open(options['stdin'], "r")
            except Exception:                                                                          
                logger.exception("Error occurred while trying to open stream "\
                    "'stdin':")
                self.context.stdin.close()
                exit(CONTEXT_ERROR)

        if options['stdout']:
            try:
                self.context.stdout = open(options['stdout'], "a+")
            except Exception:                                                                          
                logger.exception("Error occurred while trying to open stream "\
                    "'stdout':")
                self.context.stdout.close()
                exit(CONTEXT_ERROR)
        
        if options['stderr']:
            try:
                self.context.stderr = open(options['stderr'], "a+")
            except Exception:                                                                          
                logger.exception("Error occurred while trying to open stream "\
                    "'stderr':")
                self.context.stderr.close()
                exit(CONTEXT_ERROR)

        # Assingning signal handlers.
        self.context.signal_map = {
                # signal.SIGTERM: self.tear_down,
                signal.SIGHUP: self.reload_config,
                signal.SIGUSR1: self.reload_config,
                signal.SIGUSR2: self.tear_down,
        }

        logger.debug("Trying to open daemon context.")
        self.context.chroot_directory = options['chroot_directory']
        self.context.working_directory = options['working_directory']
        self.context.umask = options['umask']
        if options['uid']:
            self.context.uid = options['uid']
        if options['gid']:
            self.context.gid = options['gid']
        self.context.detach_process = options['detach_process']
        self.context.prevent_core = options['prevent_core']
        try:
            self.context.open()
        except daemon.daemon.DaemonOSEnvironmentError:
            logger.exception("Error ocurred trying to open daemon context:")
            exit(CONTEXT_ERROR)

        self.handle_daemon(*args, **options)

        logger.debug("Finishing loader process.")
        exit(SUCCESS)

    def log_params(self, options):
        """
        TODO: Add a description.
        """
        for param in options:
            value = options[param]
            if not value:
                continue
            logger.debug("'%s' = '%s'" % (param, value))

    def handle_daemon(self, *args, **options):
        """
        Perform the command's actions in the given daemon context
        """
        logger.info(">>> Daemon initialized.")
        self.log_params(options)

        #Make pid lock file
        pid = options["pidfile"]
        logger.debug("Locking PID file %s" % pid)
        self.context.pidfile = FileLock(pid)
        if self.context.pidfile.is_locked():
            logger.error("PID file is already locked (other process "\
                "running?).")
            exit(ALREADY_RUNNING_ERROR)
        try:
            try:
                self.context.pidfile.acquire(
                        timeout=settings.COLLECTOR_CONF['pidlock_timeout'])
            except LockTimeout:
                logger.exception("Can't lock PID file:")
                logger.info(">>> Daemon finished with errors.")
                exit(CONTEXT_ERROR)

            self.__start_rpc()
            logger.info(">>> Core daemon finished.")

        finally:
                self.tear_down()
