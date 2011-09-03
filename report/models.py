# models
from django.db import models

# utils
from django.utils.translation import ugettext as _
import settings
# from history.models import Snapshot

import logging


logger = logging.getLogger(__name__)


class Variable(models.Model):
    """
    """
    TYPE_CHOICES = (
            ('s', 'String'),
            ('n', 'Numeric'),
            ('b', 'Boolean')
            )
    name = models.CharField(_("Name"), max_length=50,
            help_text="Variable name")
    type = models.CharField(_("Data Type"), max_length=1,
            choices=TYPE_CHOICES, help_text="Data type of the variable.")
    description = models.CharField(_("Description"), max_length=200,
            blank=True, help_text="What this variable means.")

    def __unicode__(self):
        return u"%s" % self.name


class Section(models.Model):
    """
    """
    title = models.CharField(_("Title"), max_length=200,
            help_text="Title for this section of a report.")
    variables = models.ManyToManyField(Variable, help_text="Wich variables "\
            "are included to generate this report section.")
    period = models.PositiveIntegerField(null=True, blank=True, default=None,
            help_text="How many seconds will perform an active check to "\
                    "generate historic content. If it is 0 or not setted, "\
                    "only current values will be checked.")

    def variables_involved(self):
        return u",".join([v.name for v in self.variables.all()])

    def __unicode__(self):
        return u"%s" % self.title

    def get_current_values(self, server):
        """
        Returns the current values of all variables involved in this section
        for a given server.
        """
        server.connect()
        d = {}
        for v in self.variables.all():
            d.update(server.show_status(pattern=v.name))
        server.close()
        return d

    def get_history(self, server):
        """
        Returns all previous snapshots for all variable involved in this
        section for a given server.
        """
        return Snapshot.objects.filter(server=server, variable=v)

    def get_content(self, server):
        """
        Encapsules the workload of checking its corresponding method
        (get_current_value or get_history) by the value of 'period' field.
        """
        # return (self.get_current_values(server) if not self.period else
        #         self.get_history(server))
        pass


class Report(models.Model):
    """
    This is a full-report model. Contains a Title and all sections conforming a
    general panorama.
    """
    title = models.CharField(_("Report title"), max_length=200,
            help_text="Title for this report.")
    sections = models.ManyToManyField(Section,
            help_text="Sections conforming this report (also body).")

    def sections_involved(self):
        return u",".join([s.title for s in self.sections.all()])

    def __unicode__(self):
        return u"%s" % (self.title)

    def get_content(self, server):
        """
        Delegates to sections to check its own content to show.
        """
        return [(s, s.get_content()) for s in self.sections.all()]
