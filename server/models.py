# models
from django.db import models
from report.models import Report

# utils
from django.utils.translation import ugettext as _
import settings
import logging

# third party
import MySQLdb


logger = logging.getLogger(__name__)


class MySQLHandler(models.Model):
    """
    MySQL Server model handler (abstract).
    """
    ip = models.IPAddressField(_("IP address"), help_text="IP address where "\
            "this MySQL server instance is running.")
    port = models.PositiveIntegerField(_("Port"), default=3306, \
            help_text="Port where this instance is binded.")
    username = models.CharField(_("User name"), max_length=20, \
            help_text="User name to stablish a connection.")
    password = models.CharField(_("Password"), max_length=100, blank=True, \
            help_text="Password for this connection.")

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s:%d" % (self.ip, self.port)

    def connect(self):
        """
        Stablish a connection using current parameters.
        """
        params = {"host": self.ip, "port": self.port, "user": self.username, \
                "passwd": self.password}
        logger.info("Connecting to MySQL server with params '%s'." % \
                repr(params))
        self.conn = MySQLdb.connect(**params)

    def close(self):
        """
        Close the current connection.
        """
        try:
            self.conn.close()
        except:
            pass
        logger.debug("%s Connection closed." % self)

    def restart(self):
        self.close()
        self.connect()

    def doquery(self, sql, parsefunc=None):
        """
        Execute a query with the statement given in 'sql' parameter. Also
        'parsefunc' function is applied if it is not None.
        """
        cur = self.conn.cursor()
        logger.debug("Executing query: %s" % sql)
        cur.execute(sql)
        result = cur.fetchall()
        logger.debug("Result: %s" % repr(result))
        return parsefunc(result) if parsefunc else result

    def changedb(self, dbname=None):
        """
        Set the schema 'dbname' if not None.
        """
        if dbname:
            self.doquery("USE %s;" % dbname)

    def show_status(self, pattern=None):
        """
        Returns all server statistics variables' values matching 'pattern' if
        not None, else all.
        """
        sql = "SHOW STATUS %s;" % ("LIKE '%s'" % pattern if pattern else '')
        return self.doquery(sql, dict)


class Server(MySQLHandler):
    """
    MySQL Server instance wich will be used to generate reports.
    """
    active = models.BooleanField(_("Is active"), default=True)
    name = models.CharField(_("Name"), max_length=100, \
            help_text="Server name or ID.")
    reports = models.ManyToManyField(Report, help_text="Selected reports for "\
            "this server")

    def __unicode__(self):
        return u"%s [%s:%d]" % (self.name, self.ip, self.port)

    def show_variables(self):
        """
        Returns all system variables' values for new connections.
        """
        return self.doquery("SHOW GLOBAL VARIABLES;", dict)

    def available_reports(self):
        """
        Returns a comma separated list with the name of all reports assigned
        to this server.
        """
        return u",".join([r.title for r in self.reports.all()])

    def get_variables(self):
        """
        Returns all variables associated to this server through reports and its
        sections.
        """
        variables = set()
        for r in self.reports.all():
            for s in r.sections.all():
                for v in s.variables.all():
                    variables.add((s.period, v))
        return variables
