from django.http import (HttpResponse, HttpResponseRedirect,
        HttpResponseBadRequest, HttpRequest)
from django.shortcuts import render_to_response, Http404, get_object_or_404

from server.models import Server
from history.models import Snapshot

import logging


logger = logging.getLogger(__name__)


def show_all_reports(request, ip=None, id=None):
    """
    """

    server = get_object_or_404(Server, **({'ip': ip} if ip else {'id': id}))

    params = {'server': server, 'sections': {}}

    return render_to_response('reports.html', params)
