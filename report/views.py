from django.shortcuts import render_to_response, get_object_or_404

from server.models import ReportByServer
from history.models import Snapshot
from report.models import Section


import logging


logger = logging.getLogger(__name__)


def show_report(request, uuid=None):
    """
    """
    rs = get_object_or_404(ReportByServer, uuid=uuid)
    params = {'report': rs.report, 'sections': {}}

    for s in rs.report.sections.all():
        if not s.period:
            if rs.server.connect():
                ss = Snapshot.get_current_values(rs.server, s.variables.all())
                
                logger.debug("Current values collected for section: %s" %
                        repr(ss))
                params['sections'][s.id] = ss
            else:
                # TODO: return 500
                pass
                                                                            
        else:
            ss = Snapshot.get_history(rs.server, s.variables.all())
            logger.debug("History collected for section: %s" % repr(ss))
            params['sections'][s.id] = ss

    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('report.html', params)


def show_section(request, uuid, id):
    """
    """

    s = get_object_or_404(Section, id=id)
    rs = get_object_or_404(ReportByServer, uuid=uuid)
    params = {'section': s, 'sections': {},}
                                                                               
    if not s.period:
        if rs.server.connect():
            ss = Snapshot.get_current_values(rs.server, s.variables.all())
            
            logger.debug("Current values collected for section: %s" %
                    repr(ss))
            params['sections'][s.id] = ss
        else:
            # TODO: return 500
            pass
                                                                        
    else:
        ss = Snapshot.get_history(rs.server, s.variables.all())
        logger.debug("History collected for section: %s" % repr(ss))
        params['sections'][s.id] = ss
                                                                               
    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('section.html', params)
