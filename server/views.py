from django.shortcuts import render_to_response, get_object_or_404

from server.models import Server, ReportByServer
from history.models import Snapshot

import logging


logger = logging.getLogger(__name__)


def show_all_reports(request, ip=None, id=None):
    """
    """
    server = get_object_or_404(Server, **({'ip': ip} if ip else {'id': id}))

    params = {'server': server, 'reports': {}, 'sections': {},}
    for r in server.reports.all():
        params['reports'][r.id] = ReportByServer.objects.get(server=server,
                report=r).uuid
        for s in r.sections.all():
            if not s.period:
                if server.connect():
                    ss = Snapshot.get_current_values(server, s.variables.all())
                    
                    logger.debug("Current values collected for section: %s" %
                            repr(ss))
                    params['sections'][s.id] = ss
                else:
                    # TODO: return 500
                    pass

            else:
                ss = Snapshot.get_history(server, s.variables.all())
                logger.debug("History collected for section: %s" % repr(ss))
                params['sections'][s.id] = ss
    logger.debug("Params: %s" % repr(params))

    return render_to_response('reports.html', params)
