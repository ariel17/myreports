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
    """
    server = models.ForeignKey(Server)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def take_snapshot(cls, server, must_save=True, **kwargs):
        """
        """
        raise NotImplementedError

    @classmethod
    def get_history(cls, server, **kwargs):
        """
        """
        raise NotImplementedError

    @classmethod
    def get_current_values(cls, server, **kwargs):
        """
        """
        raise NotImplementedError


class VariableSnapshot(Snapshot):
    """
    Stores the variable value of some server in given time.
    """
    variable = models.ForeignKey(Variable)
    value = models.IntegerField()

    def __unicode__(self):
        return u"%s=%s" % (self.variable.name, self.value)

    @classmethod
    def take_snapshot(cls, server, must_save=True, **kwargs):
        """
        Takes an snapshot for the value of the given variable on this server at
        this moment.
        """
        variable = kwargs['variable']
        result = None
        if variable.data_type <> 'c': 
            value = server.show_status(pattern=variable.name)
            if len(value.keys()) == 0:  # pattern not found
                return None
            result = cls(server=server, variable=variable,
                    value=value[variable.name])
        else:
            result = []
            for d in server.do_task(variable.name):
                # u = Usage()
                pass
        if must_save and result:
            result.save()
        return result

    @classmethod
    def get_history(cls, server, **kwargs):
        """
        Returns all variables' snapshots collected for the indicated variables
        and for the given server.
        """
        return cls.objects.filter(server=server,
                variable__id__in=[v.id for v in variables['variables']])

    @classmethod
    def get_current_values(cls, server, **kwargs):
        """
        Returns current values for a given server and for all variables
        indicated.
        """
        values = []
        for v in kwargs['variables']:
            s = cls.take_snapshot(server, v, False)
            if s:
                values.append(s)


class UsageSnapshot(Snapshot):
    """
    Represents databases usage in a server. It is a representative usage,
    because it not shows completly active use per database.
    """
    database = models.CharField(_("Database"), help_text="")
    qid = models.PositiveIntegerField(_("Value"), help_text="Current value"\
            " for this date.")
    duration = models.PositiveIntegerField(_("Query time"), help_text="")


class SnapshotFactory(object):
    """
    """
    pass    
