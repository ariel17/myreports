from django.shortcuts import render_to_response, get_object_or_404

from server.models import Server, ReportByServer
from history.models import Snapshot

import logging


logger = logging.getLogger(__name__)


def show_all_reports(request, ip=None, id=None):
    """
    """
    server = get_object_or_404(Server, **({'ip': ip} if ip else {'id': id}))

    params = {
            'server': server, 
            'permalink': server.get_absolute_url(),
            'reports': {}, 
            'sections': {}, 
    }
    for r in server.reports.all():
        uuid = ReportByServer.objects.get(server=server, report=r).uuid
        params['reports'][r.id] = r.get_absolute_url(uuid)
        for s in r.sections.all():
            ss = None
            if not s.period:
                if server.connect():
                    ss = Snapshot.get_current_values(server, s.variables.all())
                    logger.debug("Current values collected for section: %s" %
                            repr(ss))
                else:
                    # TODO: return 500
                    pass
            else:
                ss = Snapshot.get_history(server, s.variables.all())
                logger.debug("History collected for section: %s" % repr(ss))
            params['sections'][s.id] = {
                    'snapshots': ss, 
                    'permalink': s.get_absolute_url(uuid)
            }
    logger.debug("Params: %s" % repr(params))

    return render_to_response('reports.html', params)
