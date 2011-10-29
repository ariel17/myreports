from django.db import models
from report.models import Report
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

    def test_connection(self):
        """
        Verifies if it is possible to connect to the server with current
        parameters. It uses the functions 'connect()' and 'close()' to perform
        the test, so be careful to call this method within an already connected
        instance.
        """
        try:
            return self.connect()
        finally:
            self.close()

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

    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('show_all_reports', (self.id,))


class ServerFactory:
    """
    TODO: add some docstring for ServerFactory
    """
    @staticmethod
    def create(**kwargs):
        """
        TODO: add some docstring for this method.
        """
        port = kwargs.get('port', None)
        if port:
            try:
                kwargs['port'] = int(port)
            except:
                message = "Can not convert to integer parameter 'port': "\
                        "'%s'" % port
                logger.exception(message)
                return None, message

        for k in ('ip', 'username', 'password'):
            if k not in kwargs:
                message = "Missing parameter: '%s'." % k
                logger.warn(message)
                return None, message

        return Server(**kwargs), None


class ReportByServer(models.Model):
    """
    """
    server = models.ForeignKey(Server)
    report = models.ForeignKey(Report)
    order = models.PositiveIntegerField(_("Order"), default=0, blank=True,
            null=True, help_text="Indicates the final position when "\
                    "presenting the information to the user. If this value "\
                    "is 0 or NULL, the order will not be garatized.")

    def __unicode__(self):
        return u"ReportByServer report_id=%d server_id=%d order=%d" % \
                (self.report.id, self.server.id, self.order)


class Database(models.Model):
    """
    docstring for database
    """
    server = models.ForeignKey(Server)
    name = models.CharField(_("Name"), max_length=200, help_text="")

    def __unicode__(self):
        return u"%s @ %s" % (self.name, self.server.name)
