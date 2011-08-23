import datetime

from django.db import models
from server.models import Server
from report.models import Variable


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
    def take_snapshot(server, variable):
        """
        Takes an snapshot for the value of the given variable on this server at
        this moment.
        """
        value = server.show_status(pattern=variable.name)
        s = Snapshot(server=server, variable=variable, 
                value=value[variable.name])
        s.save()
        return s

    def update(self):
        """
        Updates the value of the variable on the given server to the actual
        value.
        """
        self.value = self.server.show_status(pattern=self.variable.name)
        self.time = datetime.now()
        self.save()
