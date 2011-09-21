from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
import settings
import logging


logger = logging.getLogger(__name__)


class Variable(models.Model):
    """
    Represents a MySQL variable.
    """
    DATA_TYPE_CHOICES = (
            ('s', 'String'),
            ('n', 'Numeric'),
            ('b', 'Boolean'),
            ('a', 'Abstract'),
            )
    VARIABLE_TYPE_CHOICES = (
            ('m', 'MySQL Variable'),
            ('c', 'Variable as Command'),
            )
    name = models.CharField(_("Name"), unique=True, max_length=50,
            help_text="Variable name")
    data_type = models.CharField(_("Data Type"), max_length=1,
            choices=DATA_TYPE_CHOICES, help_text="Data type of the variable.")
    type = models.CharField(_("Variable Type"), max_length=1,
            choices=VARIABLE_TYPE_CHOICES, default='m', help_text="")
    description = models.CharField(_("Description"), max_length=200,
            blank=True, help_text="What this variable means.")

    def __unicode__(self):
        return u"%s (dt=%s, t=%s)" % (self.name, self.data_type, self.type)


class Section(models.Model):
    """
    Section agroups many related variables to conform a chart or showing
    current values.
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

    @models.permalink
    def get_absolute_url(self, report_server_uuid):
        return ('show_section', (report_server_uuid, self.id,))


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

    @models.permalink
    def get_absolute_url(self, report_server_uuid):
        return ('show_report', (report_server_uuid,))
