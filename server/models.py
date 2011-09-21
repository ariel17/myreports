from django.db import models
from report.models import Report
from fields import UUIDField
from django.utils.translation import ugettext as _
import settings
import logging
import MySQLdb


logger = logging.getLogger(__name__)


def to_list_dict(rs, headers):
    """
    Converts a resultset, given by 'rs' to a list of dictionaries, using
    'headers' as ordered column names.
    """
    result = []
    for row in rs:
        d = {}
        for (pos, col_name) in enumerate(headers):
            d[col_name] = row[pos]
        result.append(d)
    return result


class MySQLHandler(models.Model):
    """
    MySQL Server model handler (abstract).
    """
    ip = models.IPAddressField(_("IP address"), help_text="IP address where "\
            "this MySQL server instance is running.")
    port = models.PositiveIntegerField(_("Port"), default=3306,
            help_text="Port where this instance is binded.")
    username = models.CharField(_("User name"), max_length=20,
            help_text="User name to stablish a connection.")
    password = models.CharField(_("Password"), max_length=100, blank=True,
            help_text="Password for this connection.")
    __conn = None

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s:%d" % (self.ip, self.port)

    def connect(self):
        """
        Stablish a connection using current parameters.
        """
        if not self.__conn:
            try:
                params = {"host": self.ip, "port": self.port,
                        "user": self.username, "passwd": self.password}
                logger.info("Connecting to MySQL server with params '%s'." %
                        repr(params))
                self.__conn = MySQLdb.connect(**params)
                return True
            except Exception, (e):
                logger.exception("Can not connect to MySQL Server:")
            return False
        return True

    def close(self):
        """
        Close the current connection.
        """
        try:
            self.__conn.close()
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
        cur = self.__conn.cursor()
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

    def show_variables(self):
        """
        Returns all system variables' values for new connections.
        """
        return self.doquery("SHOW GLOBAL VARIABLES;", dict)

    def show_processlist(self):
        """
        Returns all user queries actually running.
        """
        sql = "SHOW FULL PROCESSLIST;"
        rs = self.doquery(sql)
        return to_list_dict(rs, ('id', 'user', 'host', 'db', 'command', 'time',
            'state', 'info'))


class Server(MySQLHandler):
    """
    MySQL Server instance wich will be used to generate reports.
    """
    active = models.BooleanField(_("Is active"), default=True)
    name = models.CharField(_("Name"), max_length=100, \
            help_text="Server name or ID.")
    reports = models.ManyToManyField(Report, through='ReportByServer',
            help_text="Selected reports for this server")

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
                    variables.add((s.period, v,))
        return variables

    def get_periods(self):
        """
        Determines the minimun time period for heartbeat. This period is
        determined by the Greatest Common Divisor between all specified time
        periods in sections.
        """
        def gcd(a, b):
            """
            """
            if not b:
                return 0
            if a % b == 0:
                return b
            return gcd(a, a % b)

        # only variables with numeric period (period == None means chekc only
        # current values).
        periods = [v[0] for v in self.get_variables() if v[0]]
        # based on http://code.activestate.com/recipes/577282-finding-the-
        #   gcd-of-a-list-of-numbers-aka-reducing-/
        return reduce(gcd, periods), max(periods)

    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('show_all_reports', (self.id,))


class ReportByServer(models.Model):
    """
    """
    server = models.ForeignKey(Server)
    report = models.ForeignKey(Report)
    uuid = UUIDField(editable=False)

    def __unicode__(self):
        return u"ReportByServer report_id=%d server_id=%d uuid=%s" % \
                (self.report.id, self.server.id, self.uuid)


class Database(models.Model):
    """
    docstring for database
    """
    server = models.ForeignKey(Server)
    name = models.CharField(_("Name"), max_length=200, help_text="")

    def __unicode__(self):
        return u"%s @ %s" % (self.name, self.server.name)
