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
    name = models.CharField(_("Name"), max_length=50)
    description = models.CharField(_("Description"), max_length=200)


class Section(models.Model):
    """
    """
    title = models.CharField(_("Title"), max_length=200, \
            help_text="Title for this section of a report.")
    variables = models.ManyToManyField(Variable, help_text="Wich variables \
            are included to generate this report section.")

    def __unicode__(self):
        """
        """
        return u"Section '%s' @ [%s]" % (self.title, self.report)


class Report(models.Model):
    """
    """
    title = models.CharField(_("Report title"), max_length=200, \
            help_text="Title for this report.")
    sections = models.ManyToManyField(Section, help_text="Sections conforming \
            this report.")

    def __unicode__(self):
        """
        """
        return u"Report '%s'" % (self.title)
