# models
from django.db import models

# utils
from django.utils.translation import ugettext as _
import settings
import logging


logger = logging.getLogger(__name__)

class Variable(models.Model):
    """
    """
    DTYPE_CHOICES = (
            ('s', 'String'),
            ('n', 'Numeric'),
            ('b', 'Boolean')
            )
    name = models.CharField(_("Name"), max_length=50, help_text="Variable \
            name")
    type = models.CharField(_("Data Type"), max_length=1, \
            choices=DTYPE_CHOICES, help_text="Data type of the variable.")
    description = models.CharField(_("Description"), max_length=200, \
            blank=True, help_text="What this variable means.")

    def __unicode__(self):
        return u"%s" % self.name


class Section(models.Model):
    """
    """
    title = models.CharField(_("Title"), max_length=200, \
            help_text="Title for this section of a report.")
    variables = models.ManyToManyField(Variable, help_text="Wich variables \
            are included to generate this report section.")

    def variables_involved(self):
        return u",".join([v.name for v in self.variables.all()])

    def __unicode__(self):
        return u"%s" % self.title


class Report(models.Model):
    """
    """
    title = models.CharField(_("Report title"), max_length=200, \
            help_text="Title for this report.")
    sections = models.ManyToManyField(Section, help_text="Sections conforming \
            this report.")

    def sections_involved(self):
        return u",".join([s.title for s in self.sections.all()])

    def __unicode__(self):
        return u"%s" % (self.title)
