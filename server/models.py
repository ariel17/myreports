# models
from django.db import models

# utils
from django.utils.translation import ugettext as _
import settings
import logging

# third party
import MySQLdb


logger = logging.getLogger(__name__)


class Server(models.Model):
    """
    MySQL Server instance wich will be used to generate reports.
    """
    name = models.CharField(_("Name"), max_length=100, \
            help_text="Server name or ID.")
    ip = models.IPAddressField(_("IP address"), help_text="IP address where \
            this MySQL server instance is running.")
    port = models.PositiveIntegerField(_("Port"), default=3306, \
            help_text="Port where this instance is binded.")
    username = models.CharField(_("User name"), max_length=20, \
            help_text="User name to stablish a connection.")
    password = models.CharField(_("Password"), max_length=100, \
            help_text="Password for this connection.")
    active = models.BooleanField(_("Is active"), default=True)

    def __unicode__(self):
        return u"%s [%s:%d]" % (self.name, self.ip, self.port)

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
        logger.debug("Connection closed.")

    def doquery(self, sql, parsefunc=None):
        """
        """
        cur = self.conn.cursor()
        logger.debug("Executing query: %s" % sql)
        cur.execute(sql)
        result = cur.fetchall()
        logger.debug("Result: %s" % repr(result))
        return parsefunc(result) if parsefunc else result

    def changedb(self, dbname):
        """
        """
        self.doquery("USE %s;" % dbname)

    def show_variables(self):
        """
        """
        return self.doquery("SHOW VARIABLES;", dict)

    def show_status(self):
        """
        """
        return self.doquery("SHOW STATUS;", dict)
