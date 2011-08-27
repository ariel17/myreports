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

from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Server
from history.models import Snapshot

from optparse import make_option

import daemon

from lockfile import FileLock, LockTimeout

import logging

import threading

from sys import exit

import signal

from time import sleep


logger = logging.getLogger(__name__)

SUCCESS, ALREADY_RUNNING_ERROR, CONTEXT_ERROR = range(3)


class Worker(threading.Thread):
    """
    This class wraps the Server class model with threading functionallity.
    """

    server = None
    running = True

    def __init__(self, id, server):
        super(Worker, self).__init__(name="Worker#%d" % id)
        self.server = server
        logger.info("Initialized thread. Handling server %s" % server)

    def stop(self):
        """
        Sets the flag 'running' to False. This breaks the thread loop.
        """
        self.running = False

    def reload_config(self):
        """
        Restablish the connection with MySQL server.
        """
        self.server.close()
        self.server.connect()

    def run(self):
        logger.debug("Core initialized.")
        try:
            logger.debug("Connecting to server.")
            self.server.connect()
            while self.running:
                logger.debug("Sleeping %d seconds." %
                        settings.CHECK_STATUS_PERIOD)
                sleep(settings.CHECK_STATUS_PERIOD)
                # check values for all variables of all reports assigned.
                for (s, v) in self.server.get_variables():
                    if v.type == 'n':  # only numeric status variables
                        s = Snapshot.take_snapshot(self.server, v)
                        logger.debug("Taked snapshot: %s." % s)
        except Exception:
            logger.exception("Error occoured when contacting server:")
        finally:
            logger.info("Finishing thread.")

    def __del__(self):
        if self.server:
            self.server.close()


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
    )
    help = "Starts the collector daemon and fetch status of all MySQL servers"\
            "configured.\n\nExample:\n\n"\
            "$ python manage.py --stdout=/var/log/collector.log "\
            "--stderr=/var/log/collector-error.log "\
            "--pidfile=/var/run/collector.pid"

    workers = []
    context = daemon.DaemonContext()

    def tear_down(self):
        """
        Handle to all task that must be made to close clean and fast.
        """
        logger.info("Tearing down.")
        logger.debug("Stopping all threads.")
        for w in self.workers:
            w.stop()

    def reload(self):
        """
        Reloads configuration and reconnects for all servers.
        """
        logger.info("Reloading configuration.")
        logger.debug("Reconnecting all servers.")
        for w in self.workers:
            w.reload()

    def handle(self, *args, **options):
        """
        Takes the options and starts a daemon context from them.

        Example::

            python manage.py linkconsumer --pidfile=/var/run/cb_link.pid
                --stdout=/var/log/cb/links.out --stderr=/var/log/cb/links.err

        """

        # Making basic checks for some parameters

        logger.debug("Checking required parameters.")
        for param in ['stdout', 'stderr', 'pidfile']:
            if not options.get(param, None):
                logger.error("Invalid value for parameter '%s'. Use -h to "\
                        "read help." % param)
                exit(CONTEXT_ERROR)

        # collecting parameters

        self.context.chroot_directory = options['chroot_directory']
        self.context.working_directory = options['working_directory']
        self.context.umask = options['umask']
        self.context.detach_process = options['detach_process']
        self.context.prevent_core = options['prevent_core']
        self.stdin = options['stdin']
        self.stdout = options['stdout']
        self.stderr = options['stderr']
        self.pidfile = options['pidfile']
        self.uid = options['uid']
        self.gid = options['gid']

        logger.debug("Openning streams.")
        if self.stdin:
            try:
                self.context.stdin = open(self.stdin, "r")
            except Exception:
                logger.exception("Error occurred while trying to open stream "\
                    "'stdin':")
                self.context.stdin.close()
                exit(CONTEXT_ERROR)

        try:
            self.context.stdout = open(self.stdout, "a+")
        except Exception:
            logger.exception("Error occurred while trying to open stream "\
                "'stdout':")
            self.context.stdout.close()
            exit(CONTEXT_ERROR)

        try:
            self.context.stderr = open(self.stderr, "a+")
        except Exception:
            logger.exception("Error occurred while trying to open stream "\
                "'stderr':")
            self.context.stderr.close()
            exit(CONTEXT_ERROR)

        # Adding signals handling

        logger.debug("Assingning signal handlers.")
        self.context.signal_map = {
                signal.SIGTERM: self.tear_down,
                signal.SIGHUP: 'terminate',
                signal.SIGUSR1: self.reload_config,
                signal.SIGUSR2: self.tear_down,
        }

        logger.debug("Trying to open daemon context.")
        try:
            self.context.open()
        except daemon.daemon.DaemonOSEnvironmentError, e:
            logger.exception("Error ocurred trying to open daemon context:")
            exit(CONTEXT_ERROR)

        self.handle_daemon(*args, **options)

        logger.debug("Finishing loader process.")
        exit(SUCCESS)

    def handle_daemon(self, *args, **options):
        """
        Perform the command's actions in the given daemon context
        """
        logger.info(">>> Daemon initialized.")

        logger.debug("'chroot_directory': %s" % self.context.chroot_directory)
        logger.debug("'working_directory': %s" %
                self.context.working_directory)
        logger.debug("'umask': %d" % self.context.umask)
        logger.debug("'detach_process': %s" % self.context.detach_process)
        logger.debug("'prevent_core': %s" % self.context.prevent_core)
        logger.debug("'stdin': %s" % self.stdin)
        logger.debug("'stdout': %s" % self.stdout)
        logger.debug("'stderr': %s" % self.stderr)
        logger.debug("'pidfile': %s" % self.pidfile)
        logger.debug("'uid': %s" % self.uid)
        logger.debug("'gid': %s" % self.gid)

        #Make pid lock file
        logger.debug("Locking PID file %s" % self.pidfile)
        self.context.pidfile = FileLock(self.pidfile)
        if self.context.pidfile.is_locked():
            logger.error("PID file is already locked (other process "\
                "running?).")
            exit(ALREADY_RUNNING_ERROR)
        try:
            self.context.pidfile.acquire(timeout=settings.PID_LOCK_TIMEOUT)
        except LockTimeout:
            self.context.pidfile.release()
            logger.exception("Can't lock PID file:")
            logger.info(">>> Daemon finished with errors.")
            exit(CONTEXT_ERROR)

        servers = Server.objects.filter(active=True)
        logger.debug("Servers fetched: %s" % repr(servers))

        logger.info("Starting threads.")
        for i in range(len(servers)):
            w = Worker(i, servers[i])
            w.start()
            self.workers.append(w)

        logger.debug("Waiting for threads to terminate.")
        for w in self.workers:
            w.join()

        logger.info(">>> Core daemon finished.")
