from django.http import (HttpRequest, HttpResponse, HttpResponseRedirect,
        HttpResponseBadRequest)
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
    for r in server.reports.all():
        for s in r.sections.all():
            if not s.period:
                ss = Snapshot.get_current_values(server, s.variables.all())
                logger.debug("Current values collected for section: %s" %
                        repr(ss))
                params['sections'][s.id] = ss
            else:
                ss = Snapshot.get_history(server, s.variables.all())
                logger.debug("History collected for section: %s" % repr(ss))
                params['sections'][s.id] = ss
    logger.debug("Params: %s" % repr(params))

    return render_to_response('reports.html', params)
