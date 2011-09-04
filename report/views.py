from django.http import (HttpResponse, HttpResponseRedirect,
        HttpResponseBadRequest, HttpRequest)
from django.shortcuts import render_to_response, Http404, get_object_or_404

from report.models import Report, Section
from server.models import Server


def show_report(request, report_id, server_id):
    """
    """
    report = get_object_or_404(Report, id=report_id)
    server = get_obejct_or_404(Server, id=server_id)
    render_to_response('report.html')


def show_section(request, section_id, server_id):
    """
    """
    section = get_object_or_404(Section, id=section_id)
    server = get_obejct_or_404(Server, id=server_id)
    return render_to_response('section.html')
