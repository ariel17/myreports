from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from server.models import Server, ServerFactory, ReportByServer
import simplejson
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
    logger.debug("Fetching reports.")
    for r in server.reports.all():
        uuid = ReportByServer.objects.get(server=server, report=r).uuid
        params['reports'][r.id] = r.get_absolute_url(uuid)
        for s in r.sections.all():
            logger.debug("Section: %s" % s)
            variables = s.variables.all()
            logger.debug("Variables in this section: %s" % repr(variables))
            if s.current:
                logger.debug("Fetching current values.")
            else:
                logger.debug("Fetching history.")
            params['sections'][s.id] = {
                    'permalink': s.get_absolute_url(uuid)
            }
    logger.debug("Params: %s" % repr(params))

    return render_to_response('reports.html', params)


def test_connection(request):
    """
    Tests a MySQL connection. Parameters spected are 'ip', 'username' and
    'password'; returns a boolean result in JSON format.
    """

    s, message = ServerFactory.create(**request.REQUEST)
    if not s:
        d = {"result": False, "message": message, }
    else:
        test = s.test_connection()
        d = {"result": test, "message": "Test connection successful" if test
                else "Invalid credentials"}

    json = simplejson.dumps(d)
    logger.info("Response for test connection: %s" % json)
    return HttpResponse(json, mimetype='application/json')
