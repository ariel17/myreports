#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Classes and data models for Django application 'report'.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
import settings
import logging


logger = logging.getLogger(__name__)


THRESHOLD_SEPARATOR = ","


class Variable(models.Model):
    """
    It represents a variable as it is.
    """
    name = models.CharField(_("Name"), unique=True, max_length=50,
            help_text="Variable name")
    description = models.CharField(_("Description"), max_length=200,
            blank=True, help_text="What this variable means.")
    query = models.CharField(_("As query"), max_length=200, blank=True,
            help_text="Use this query as variable.")
    current = models.BooleanField(_("Only current values"), default=False,
            help_text="If `True` only current values will be shown for this "\
                    "variable.")

    def __unicode__(self):
        return u"%s" % self.name


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
    thresholds = models.CharField(_("Thresholds"), blank=True, null=True,
            max_length=255, help_text="Establish limits for this variable. "\
                    "Use the format: "\
                    "&lt;value&gt;:&#35;&lt;hexa_color&gt;:&lt;legend&gt;%s..."
                    % THRESHOLD_SEPARATOR)

    def variables_involved(self):
        return u",".join([v.name for v in self.variables.all()])

    def __unicode__(self):
        return u"%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('show_section_id', (self.id,))

    def parse_threshold(self):
        """
        Returns a list with threshold content parsed.
        """
        if self.thresholds:
            return " ".join(["HRULE:%s" % t for t in \
                self.thresholds.strip().split(THRESHOLD_SEPARATOR)])
        return ""


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
    def get_absolute_url(self):
        return ('show_report_id', (self.id,))


class SectionByReport(models.Model):
    """
    """
    section = models.ForeignKey(Section)
    report = models.ForeignKey(Report)
    order = models.PositiveIntegerField(_("Order"), default=0, blank=True,
            null=True, help_text="Indicates the final position when "\
                    "presenting the information to the user. If this value "\
                    "is 0 or NULL, the order will not be garatized.")

    def __unicode__(self):
        return u"SectionByReport report_id=%d section_id=%d order=%d" % \
                (self.report.id, self.section.id, self.order)

    class Meta:
        verbose_name_plural = "Sections Assigned"
