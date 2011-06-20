# models
from django.db import models
from server.models import Server

# utils
from django.utils.translation import ugettext as _
import settings
import logging


logger = logging.getLogger(__name__)


class Report(models.Model):
    """
    """
    server = models.ForeignKey(Server)
    title = models.CharField(_("Report title"), help_text="Title for this \
            report.")

    def __unicode__(self):
        """
        """
        return u"Report '%s'" % (self.title)


class Section(models.Model):
    """
    """
    report = models.ForeignKey(Report)
    title = models.CharField(_("Part title"), help_text="Title for this \
            section of the report.")
    variables = models.CharField(_("Variables"), help_text="Variables involved \
            in this section.")

    def __unicode__(self):
        """
        """
        return u"Section '%s' for %s" % (self.title, self.report)
