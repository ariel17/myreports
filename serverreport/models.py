from django.db import models

from server.models import Server
from report.models import Report


class ServerReport(object):
    """
    """
    server = models.ForeignKey(Server)
    reports = models.ManyToManyField(Report, help_text="Selected reports for "\
            "this server")

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
                   variables.add((s.period, v, s.period))
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
           if b == 0:
               return 0
           if a % b == 0:
               return b
           return gcd(a, a % b)
                                                                               
       # only variables with numeric period (period == None means chekc only
       # current values).
       periods = [v[0] for v in self.get_variables() if v[2] is not None]
       # based on http://code.activestate.com/recipes/577282-finding-the-
       #   gcd-of-a-list-of-numbers-aka-reducing-/
       return reduce(gcd, periods), max(periods)
