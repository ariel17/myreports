from django.db import models
from server.models import Server
from report.models import Variable

class History(models.Model):
    """
    """
    server = models.ForeignKey(Server)
    variable = models.ForeignKey(Variable)
    time = models.DateTimeField(auto_now=True)
    value = models.IntegerField()

    def __unicode__(self):
        return u"%s=%s" % (self.variable.name, self.value)
