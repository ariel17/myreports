import datetime

from django.db import models
from server.models import Server
from report.models import Variable

import logging


logger = logging.getLogger(__name__)


# TODO ADD a cache table:

# hash (server id + variable id) variable-value
# stores lasts checked values for all variables.
# also add to history (or snapshot, whatever) those checks.

# for last status, check cache table.


class Snapshot(models.Model):
    """
    Stores the variable value of some server in given time.
    """
    server = models.ForeignKey(Server)
    variable = models.ForeignKey(Variable)
    time = models.DateTimeField(auto_now=True)
    value = models.IntegerField()

    def __unicode__(self):
        return u"%s=%s" % (self.variable.name, self.value)

    @staticmethod
    def take_snapshot(server, variable, must_save=True):
        """
        Takes an snapshot for the value of the given variable on this server at
        this moment.
        """
        value = server.show_status(pattern=variable.name)
        if len(value.keys()) == 0:  # pattern not found
            return None
        s = Snapshot(server=server, variable=variable,
                value=value[variable.name])
        if must_save:
            s.save()
        return s

    @staticmethod
    def get_history(server, variables):
        """
        Returns all variables' snapshots collected for the indicated variables
        and for the given server.
        """
        return Snapshot.objects.filter(server=server, 
                variable__id__in=[v.id for v in variables])

    @staticmethod
    def get_current_values(server, variables):
        """
        Returns current values for a given server and for all variables
        indicated.
        """
        values = []
        for v in variables:
            s = Snapshot.take_snapshot(server, v, False)
            if s:
                values.append(s)

    def update(self):
        """
        Updates the value of the variable on the given server to the actual
        value.
        """
        self.value = self.server.show_status(pattern=self.variable.name)
        self.time = datetime.now()
        self.save()


class Usage(models.Model):
    """
    Represents databases usage in a server. It is a representative usage,
    because it not shows completly active use per database.
    """
    server = models.ForeignKey(Server)
    database = models.CharField(_("Database"), help_text="")
    datetime = models.DateField(_("Date"), help_text="")
    qid = models.PositiveIntegerField(_("Value"), help_text="Current value"\
            " for this date.")
    time = models.PositiveIntegerField(_("Query time"), help_text="")
