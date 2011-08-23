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
    if not ip and not id:
        pass

    server = get_object_or_404(Server, **({'ip': ip} if ip else {'id': id}))
    ss = Snapshot.objects.filter(server=server)[:len(server.get_variables())]
    logger.debug(ss)
    
    return render_to_response('reports.html', {'server': server})
