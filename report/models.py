# models
from django.db import models

from django.conf import settings

# utils
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
            ('c', 'Custom Variable'),
            )
    name = models.CharField(_("Name"), unique=True, max_length=50,
            help_text="Variable name")
    data_type = models.CharField(_("Data Type"), max_length=1,
            choices=TYPE_CHOICES, help_text="Data type of the variable.")
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

    def __remove_usage_sections(self):
        """
        Removes all sections using the variable 'USAGE', if some.
        """
        try:
            id = Variable.objects.get(name='USAGE').id
        except Variable.DoesNotExist:
            return
        sections = set()
        [sections.add(s) for s in self.sections for s.variables.filter(id=id)]
        while(len(sections) > 0):
            s = sections.pop()
            s.delete()

    def __add_usage_section(self):
        """
        Adds the usage section and the variable 'USAGE' if it not exists.
        """
        v = None
        try:
            v = Variable.objects.get(name='USAGE')
        except Variable.DoesNotExist:
            v = Variable(name="USAGE", data_type='a', type='m',
                    description="Indicates to collector daemon to store "\
                            "database usage for statistics.")
        s = Section(name="Usage Section")
        s.variables.add(v)
        s.period = settings.DEFAULT_PERIOD

    def save(self):
        if not self.with_usage:
            self.__remove_usage_sections()
        else:
            self.__add_usage_section()
        super(Report, self).save()                
