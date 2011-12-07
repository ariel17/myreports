from django.shortcuts import render_to_response, get_object_or_404
from server.models import ReportByServer
from report.models import Section
import logging


logger = logging.getLogger(__name__)


def show_report(request, id=None, name=None):
    """TODO: add some docstring for show_report"""
    pass


def show_section(request, id=None, name=None, report_id=None):
    """TODO: add some docstring for show_section"""
    pass
