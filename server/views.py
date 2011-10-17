from django.shortcuts import render_to_response, get_object_or_404
from server.models import Server, ReportByServer
from history.models import VariableSnapshot
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
                ss = VariableSnapshot.get_current_values(server,
                        variables=variables)
                logger.debug("Current values collected for section: %s" %
                        repr(ss))
            else:
                logger.debug("Fetching history.")
                ss = VariableSnapshot.get_history(server, variables=variables)
                logger.debug("History collected for section: %s" % repr(ss))
            params['sections'][s.id] = {
                    'snapshots': ss,
                    'permalink': s.get_absolute_url(uuid)
            }
    logger.debug("Params: %s" % repr(params))

    return render_to_response('reports.html', params)


def test_connection(request):
    """
    Tests a MySQL connection. Returns a boolean result in JSON format.
    """
    params = {"ip": False, "user": False, "password": False, }
    for p in params:
        if p in request.REQUEST:
            params[p] = request.REQUEST[p]
        else:
            logger.warning("Missing parameter for request to test "\
                    "connection: '%s'" % p)
            json = simplejson.dumps({"result": False, })
            return HttpResponse(json, mimetype='application/json')
                

    logger.info("Request to test connection with parameters: %s" % repr(params))

    s = Server(**params)
    json = simplejson.dumps({"result": self.test_connection(), })

    logger.info("Response: %s" % json)
    return HttpResponse(json, mimetype='application/json')
