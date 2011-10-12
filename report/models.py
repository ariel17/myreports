from django.db import models
from django.conf import settings
from utils.fields import UUIDField
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
    type = models.CharField(_("Variable Type"), max_length=1, default='m',
            choices=VARIABLE_TYPE_CHOICES, help_text="")
    description = models.CharField(_("Description"), max_length=200,
            blank=True, help_text="What this variable means.")

    def __unicode__(self):
        return u"%s (dt=%s, t=%s)" % (self.name, self.data_type, self.type)


class WithText(models.Model):
    """
    An absctract class for positionable elements, such reports or sections.
    """
    title = models.CharField(_("Title"), max_length=100,
            help_text="Title for this element.")
    subtitle = models.CharField(_("Subtitle"), blank=True, null=True,
            max_length=200, help_text="Subtitle for this element.")

    class Meta:
        abstract = True


class Section(WithText):
    """
    Section agroups many related variables to conform a chart or showing
    current values.
    """
    variables = models.ManyToManyField(Variable, help_text="Wich variables "\
            "are included to generate this report section.")
    order = models.PositiveIntegerField(_("Order"), default=0, blank=True,
            null=True, help_text="Indicates the final position when "\
                    "presenting the information to the user. If this value "\
                    "is 0 or NULL, the order will not be garatized.")
    current = models.BooleanField(_("Only current?"), default=False,
            help_text="If `True`, it field indicates that this section only "\
                    "shows the current values for all variables in it.")

    def variables_involved(self):
        return u",".join([v.name for v in self.variables.all()])

    def __unicode__(self):
        return u"%s" % self.title

    @models.permalink
    def get_absolute_url(self, report_server_uuid):
        return ('show_section', (report_server_uuid, self.id,))


class Report(WithText):
    """
    This is a full-report model. Contains a Title and all sections conforming a
    general panorama.
    """
    sections = models.ManyToManyField(Section, through='SectionByReport',
            help_text="Sections conforming this report (also body).")

    def sections_involved(self):
        return u",".join([s.title for s in self.sections.all()])

    def __unicode__(self):
        return u"%s" % (self.title)

    @models.permalink
    def get_absolute_url(self, report_server_uuid):
        return ('show_report', (report_server_uuid,))


class SectionByReport(models.Model):
    """
    """
    section = models.ForeignKey(Section)
    report = models.ForeignKey(Report)
    order = models.PositiveIntegerField(_("Order"), default=0, blank=True,
            null=True, help_text="Indicates the final position when "\
                    "presenting the information to the user. If this value "\
                    "is 0 or NULL, the order will not be garatized.")
    uuid = UUIDField(editable=False)

    def __unicode__(self):
        return u"SectionByReport report_id=%d section_id=%d order=%d "\
                "uuid=%s" % (self.report.id, self.section.id, self.order,
                        self.uuid)
