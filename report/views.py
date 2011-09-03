from django.http import (HttpResponse, HttpResponseRedirect,
        HttpResponseBadRequest, HttpRequest)
from django.shortcuts import render_to_response, Http404, get_object_or_404

from report.models import Section


def show_report(request, id):
    """
    """
    pass


def show_section(request, id):
    """
    """
    section = get_object_or_404(Section, id=id)
    return render_to_response('section.html')
