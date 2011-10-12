from django.shortcuts import render_to_response, get_object_or_404
from server.models import ReportByServer
from history.models import VariableSnapshot
from report.models import Section
import logging


logger = logging.getLogger(__name__)


def show_report(request, uuid):
    """
    """
    rs = get_object_or_404(ReportByServer, uuid=uuid)
    params = {
            'name': 'report',
            'title': rs.report.title,
            'subtemplate': 'report.html',
            'server': rs.server,
            'report': rs.report,
            'reports': {rs.report.id: rs.report.get_absolute_url(uuid), },
            'sections': {},
    }

    for s in rs.report.sections.all():
        ss = None
        if s.current:
            if rs.server.connect():
                ss = VariableSnapshot.get_current_values(rs.server,
                        variables=s.variables.all())
                logger.debug("Current values collected for section: %s" %
                        repr(ss))
            else:
                # TODO: return 500
                pass
        else:
            ss = VariableSnapshot.get_history(rs.server,
                    variable=s.variables.all())
            logger.debug("History collected for section: %s" % repr(ss))
        params['sections'][s.id] = {
                'snapshots': ss,
                'permalink': s.get_absolute_url(uuid)
        }

    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('direct.html', params)


def show_section(request, uuid, id):
    """
    """

    s = get_object_or_404(Section, id=id)
    rs = get_object_or_404(ReportByServer, uuid=uuid)
    params = {
            'name': 'section',
            'title': s.title,
            'subtemplate': 'section.html',
            'server': rs.server,
            'section': s,
            'sections': {},
    }

    ss = None
    if s.current:
        if rs.server.connect():
            ss = VariableSnapshot.get_current_values(rs.server,
                    variables=s.variables.all())
            logger.debug("Current values collected for section: %s" %
                    repr(ss))
        else:
            # TODO: return 500
            pass
    else:
        ss = VariableSnapshot.get_history(rs.server,
                variables=s.variables.all())
        logger.debug("History collected for section: %s" % repr(ss))

    params['sections'][s.id] = {
            'snapshots': ss,
            'permalink': s.get_absolute_url(uuid)
    }

    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('direct.html', params)
