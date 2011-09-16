from django.db import models
from django.db.models.signals import pre_save
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
            ('u', 'Variable for Usage'),
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
        return u"%s (%s)" % (self.name, self.type)


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
    with_usage = models.BooleanField(_("With usage?"), default=False,
            help_text="")

    def sections_involved(self):
        return u",".join([s.title for s in self.sections.all()])

    def __unicode__(self):
        return u"%s" % (self.title)

    @models.permalink
    def get_absolute_url(self, report_server_uuid):
        return ('show_report', (report_server_uuid,))

    @staticmethod
    def remove_usage_sections(report, *args, **kwargs):
        """
        Removes all sections using the variable 'USAGE', if some.
        """
        try:
            id = Variable.objects.get(name='USAGE').id
        except Variable.DoesNotExist:
            return
        for s in Section.objects.filter(variables__in=[id,]):
            if s in report.sections.all():
                report.sections.remove(s)

    @staticmethod
    def add_usage_section(report, *args, **kwargs):
        """
        Adds the usage section and the variable 'USAGE' if it not exists.
        """
        v = None
        try:
            v = Variable.objects.get(name='USAGE')
        except Variable.DoesNotExist:
            v = Variable(name="USAGE", data_type='a', type='c',
                    description="Indicates to collector daemon to store "\
                            "database usage for statistics.")
            v.save()
        try:
            s = Section.objects.get(variables__in=[v.id,])
        except Section.DoesNotExist:
            s = Section(title="Usage Section", period=settings.DEFAULT_PERIOD)
            s.save()
            s.variables.add(v)
            s.save()
        report.sections.add(s)
                                                                                
    @staticmethod
    def check_usage_section(sender, *args, **kwargs):
        obj = kwargs['instance']
        print obj
        logger.debug("Hola")
        if not obj.with_usage:
            Report.remove_usage_sections(obj)
        else:
            Report.add_usage_section(obj)


pre_save.connect(Report.check_usage_section, sender=Report)
