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

from optparse import make_option

import daemon

from lockfile import FileLock

import logging

import threading

from sys import exit


logger = logging.getLogger(__name__)

SUCCESS, ALREADY_RUNNING, NO_PIDFILE, CANT_LOCK_PID, CONTEXT_ERROR = \
        range(5)


class Worker(threading.Thread):
    """
    This class wraps the Server class model with threading functionallity.
    """
    id = None
    server = None

    def __init__(self, id, server):
        super(Worker, self).__init__()
        self.id = id
        self.server = server
        logger.info("Worker#%d - Initialized thread. Handling server %s" %
                (id, server))

    def run(self):
        # TODO: while True? (condition? signals?)
        # TODO: in threads: sleep (settings.CHECK_STATUS_PERIOD)
        # TODO: in threads: check statistics.
        pass

    def __del__(self):
        if self.server:
            self.server.close()
        logger.info(("Worker#%d - " % self.id if self.id else "") +
                "Thread finished.")


class Command(BaseCommand):  # DaemonCommand

    option_list = BaseCommand.option_list + (
        make_option('--chroot_directory', action='store', default=None,
            dest='chroot_directory', help='Full path to a directory to set as \
                    the effective root directory of the process.'),
        make_option('--working_directory', action='store',
            dest='working_directory', default="/", help='Full path of the \
                    working directory to which the process should change on \
                    daemon start.'),
        make_option('--umask', action='store', dest='umask', default=0,
            type="int", help='File access creation mask ("umask") to set for \
                    the process on daemon start.'),
        make_option('--pidfile', action='store', dest='pidfile', default=None,
            help='Context manager for a PID lock file. When the daemon \
                    context opens and closes, it enters and exits the \
                    `pidfile` context manager.'),
        make_option('--detach_process', action='store', default=True,
            dest='detach_process', help='If ``True``, detach the process \
                    context when opening the daemon context; if ``False``, \
                    do not detach.'),
        make_option('--uid', action='store', dest='uid', help='The user ID \
                ("UID") value to switch the process to on daemon start.',
                default=None),
        make_option('--gid', action='store', dest='gid', help='The group ID \
                ("GID") value to switch the process to on daemon start.',
                default=None),
        make_option('--prevent_core', action='store', dest='prevent_core',
            default=True, help='If true, prevents the generation of core \
                    files, in order to avoid leaking sensitive information \
                    from daemons run as `root`.'),
        make_option('--stdin', action='store', dest='stdin', default=None,
            help='Standard In'),
        make_option('--stdout', action='store', dest='stdout', default=None,
            help='Standard Out'),
        make_option('--stderr', action='store', dest='stderr', default=None,
            help='Standard Error'),
    )
    help = "Starts the collector daemon and fetch status of all MySQL servers \
            configured."

    context = daemon.DaemonContext()

    def handle(self, *args, **options):
        """
        Takes the options and starts a daemon context from them.

        Example::

            python manage.py linkconsumer --pidfile=/var/run/cb_link.pid
                --stdout=/var/log/cb/links.out --stderr=/var/log/cb/links.err

        """

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

        #Get file objects
        try:
            if self.stdin is not None:
                self.context.stdin = open(self.stdin, "r")
                                                                               
            if self.stdout is not None:
                self.context.stdout = open(self.stdout, "a+")
                                                                               
            if self.stderr is not None:
                self.context.stderr = open(self.stderr, "a+")
        except Exception:
            logger.exception("Error occurred while trying to open an output:")
            sys.exit(CONTEXT_ERROR)

        try:
            self.context.open()
        except daemon.daemon.DaemonOSEnvironmentError, e:
            logger.exception("Error ocurred trying to open daemon context:")
            exit(CONTEXT_ERROR)

        self.handle_daemon(*args, **options)

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
        if self.pidfile:
            logger.debug("Locking PID file %s" % self.pidfile)
            self.context.pidfile = FileLock(self.pidfile)
            if self.context.pidfile.is_locked():
                logger.error("PID file is already locked (other process \
                        running?).")
                exit(ALREADY_RUNNING)
            try:
                self.context.pidfile.acquire(timeout=settings.PID_LOCK_TIMEOUT)
            except lockfile.LockTimeout:
                self.context.pidfile.release()
                logger.exception("Can't lock PID file:")
                logger.info(">>> Daemon finished with errors.")
                exit(CANT_LOCK_PID)
        else:
            logger.error("Invalid value for 'pidfile' parameter.")
            logger.info(">>> Daemon finished with errors.")
            exit(NO_PIDFILE)

        servers = Server.objects.filter(active=True)
        logger.debug("Servers fetched: %s" % repr(servers))

        workers = []

        logger.info("Starting threads.")
        for i in range(len(servers)):
            w = Worker(i, servers[i])
            w.start()
            workers.append(w)

        logger.info("Stopping threads.")
        for w in workers:
            w.join()

        logger.info(">>> Core daemon finished.")
