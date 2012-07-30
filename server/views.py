#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: TODO
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


import logging
import simplejson

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from server.models import Server, ServerFactory, ReportByServer


logger = logging.getLogger(__name__)


def show_all_servers(request):
    """
    """
    return show_reports(request, Server.objects.filter(active=True),
            with_general_index=True)


def show_server_id(request, id):
    """
    """
    return show_reports(request, [get_object_or_404(Server, id=id), ])


def show_server_ip(request, ip):
    """
    """
    return show_reports(request, [get_object_or_404(Server, ip=ip), ])


def show_server_name(request, name):
    """
    """
    return show_reports(request, get_object_or_404(Server, name=name))


def show_reports(request, servers, with_general_index=False):
    ss = []
    for s in servers:
        p = {
            'server': s,
            'permalink': s.get_absolute_url(),
            'reports': [],
            }
        for r in s.reports.all():
            rbs = ReportByServer.objects.get(server=s, report=r)
            rd = {
                    'permalink': r.get_absolute_url(),
                    'rbs': rbs,
                    'report': r,
                    'sections': [],
                    }
            for se in r.sections.all():
                sd = {
                        'permalink': se.get_absolute_url(),
                        'section': se,
                        'variables': [],
                        }
                for v in se.variables.all():
                    sd['variables'].append({
                            'minutes': "s%dv%d.rrd-minutes.png" % (s.id, v.id),
                            'hourly': "s%dv%d.rrd-hourly.png" % (s.id, v.id),
                            'daily': "s%dv%d.rrd-daily.png" % (s.id, v.id),
                            'weekly': "s%dv%d.rrd-weekly.png" % (s.id, v.id),
                            'monthly': "s%dv%d.rrd-monthly.png" % (s.id, v.id),
                            'yearly': "s%dv%d.rrd-yearly.png" % (s.id, v.id)})
                rd['sections'].append(sd)
            p['reports'].append(rd)
        ss.append(p)

    logger.debug("Rendering: %s" % repr(ss))
    return render_to_response('reports.html', \
            {'servers': ss, 'with_general_index': with_general_index},
            context_instance=RequestContext(request, {'CRONTAB_TIME_LAPSE':
                settings.CRONTAB_TIME_LAPSE,}))


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
