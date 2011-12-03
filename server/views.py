from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from server.models import Server, ServerFactory, ReportByServer
import simplejson
import logging


logger = logging.getLogger(__name__)


def show_all_servers(request):
    """
    """
    return show_reports(request, Server.objects.filter(active=True))


def show_server_id(request, id):
    """
    """
    return show_reports(request, [get_object_or_404(Server, id=id),])


def show_server_ip(request, ip):
    """
    """
    return show_reports(request, [get_object_or_404(Server, ip=ip),])


def show_server_name(request, name):
    """
    """
    return show_reports(request, get_object_or_404(Server, name=name))


def show_reports(request, servers):
    info = []
    for s in servers:
        p = {
            'server': s,
            'permalink': s.get_absolute_url(),
            'reports': {},
            'sections': {},
            }
        for r in s.reports.all():
            rbs = ReportByServer.objects.get(server=s, report=r)
            p['reports'][r.id] = r.get_absolute_url()
            for se in r.sections.all():
                variables = se.variables.all()
                p['sections'][s.id] = {
                        'permalink': s.get_absolute_url(),}
                        # s.get_absolute_url(rbs.id),}
        info.append(p)                
    logger.debug("Params: %s" % repr(p))

    return render_to_response('reports.html', p)


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
