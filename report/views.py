from django.shortcuts import render_to_response, get_object_or_404
from server.models import ReportByServer
from report.models import Section
import logging


logger = logging.getLogger(__name__)


def show_report(request, id):
    """
    """
    rs = get_object_or_404(ReportByServer, id=id)
    params = {
            'name': 'report',
            'title': rs.report.title,
            'subtemplate': 'report.html',
            'server': rs.server,
            'report': rs.report,
            'reports': {rs.report.id: rs.report.get_absolute_url(id),},
            'sections': {},
    }

    for s in rs.report.sections.all():
        ss = None
        if s.current:
            if rs.server.connect():
                pass
            else:
                # TODO: return 500
                pass
        else:
            logger.debug("History collected for section: %s" % repr(ss))
        params['sections'][s.id] = {
                'permalink': s.get_absolute_url(id, s.id)
        }

    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('direct.html', params)


def show_section(request, reportbyserver_id, section_id):
    """
    """
    s = get_object_or_404(Section, id=section_id)
    rs = get_object_or_404(ReportByServer, id=reportbyserver_id)
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
            pass
        else:
            # TODO: return 500
            pass
    else:
        pass

    params['sections'][s.id] = {
            'permalink': s.get_absolute_url(reportbyserver_id, s.id)
    }

    logger.debug("Params to use: %s" % repr(params))
    return render_to_response('direct.html', params)
