# This model file implements the factory pattern to determine with Snapshot
# class must be instantiated. This particular approach is based in
# this StackOverflow thread:
#
# http://stackoverflow.com/questions/456672/class-factory-in-python
#
# Thank you Alec Thomas!


from django.db import models
from server.models import Server, Database
from report.models import Variable
from datetime import date
from django.utils.translation import ugettext as _
import logging


logger = logging.getLogger(__name__)


class Snapshot(models.Model):
    """
    """
    time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def is_snapshot_for(cls, variable):
        """
        """
        raise NotImplementedError

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
    server = models.ForeignKey(Server)
    variable = models.ForeignKey(Variable)
    value = models.IntegerField()

    def __unicode__(self):
        return u"%s=%s" % (self.variable.name, self.value)

    @classmethod
    def is_snapshot_for(cls, variable):
        """
        """
        return variable.type != 'c'

    @classmethod
    def take_snapshot(cls, server, must_save=True, **kwargs):
        """
        Takes an snapshot for the value of the given variable on this server at
        this moment.
        """
        variable = kwargs['variable']
        value = server.show_status(pattern=variable.name)
        if len(value.keys()) == 0:  # pattern not found
            return None
        result = cls(server=server, variable=variable,
                value=value[variable.name])
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
                variable__id__in=[v.id for v in kwargs['variables']])

    @classmethod
    def get_current_values(cls, server, **kwargs):
        """
        Returns current values for a given server and for all variables
        indicated.
        """
        values = []
        for v in kwargs['variables']:
            s = cls.take_snapshot(server, must_save=False, variable=v)
            if s:
                values.append(s)
        return values


class UsageSnapshot(Snapshot):
    """
    Represents databases usage in a server. It is a representative usage,
    because it not shows completly active use per database.
    """
    database = models.ForeignKey(Database)
    qid = models.PositiveIntegerField(_("Value"), help_text="Current value"\
            " for this date.")
    duration = models.PositiveIntegerField(_("Query time"), help_text="")

    def __unicode__(self):
        return u"Database='%s' qid=%s d=%s time='%s'" % (self.database,
                self.qid, self.duration, self.time)

    @classmethod
    def take_snapshot(cls, server, must_save=True, **kwargs):
        """
        """
        result = []
        for u in server.show_processlist():
            if not u['db']:
                continue
            logger.debug("Usage: %s" % repr(u))
            qid, duration = int(u['id']), int(u['time'])
            try:
                db = Database.objects.get(server__id=server.id, name=u['db'])
            except Database.DoesNotExist:
                db = Database(server=server, name=u['db'])
                if must_save:
                    db.save()
            try:
                s = cls.objects.get(database__id=db.id, qid=qid,
                        duration__lte=duration, time__gte=date.today())
            except cls.DoesNotExist:
                s = cls(database=db, qid=qid, duration=duration)
                if must_save:
                    s.save()
            result.append(s)
        return result

    @classmethod
    def is_snapshot_for(cls, variable):
        """
        """
        return variable.type == 'c' and variable.name == 'USAGE'


class SnapshotFactory(object):
    """
    """
    @classmethod
    def take_snapshot(cls, server, must_save=True, **kwargs):
        for c in Snapshot.__subclasses__():
            if c.is_snapshot_for(kwargs['variable']):
                return c.take_snapshot(server, must_save, **kwargs)
        return None
