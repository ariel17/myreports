#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Dumps graphics from RRDTool for all sections into image files.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"

import os
import datetime 
import time
import logging
from sys import exit
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Server
from report.models import Variable

import collector.rrd as rrdtool


logger = logging.getLogger(__name__)

SUCCESS, MISSING_PARAMETERS_ERROR = range(2)
DAY_MINUTES = 60 * 24  # sec x min x hs


class BasicCache(object):
    """
    TODO: add some docstring for BasicCache
    """
    cache = {}

    def set(self, obj):
        """TODO: add some docstring for set"""
        self.cache.setdefault(obj.__class__.__name__, {})[obj.id] = obj
        return obj

    def get(self, cl, id):
        """TODO: add some docstring for get"""
        objs = self.cache.get(cl.__name__, None)
        obj = objs.get(id, None) if objs else None
        return obj if obj else self.set(cl.objects.get(id=id))


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--img-path', '-p', action='store', dest='img-path',
            default=settings.GRAPH_DIR, help="Path to store RRDTool images. "\
                    "Default: %s" % settings.GRAPH_DIR),
        make_option('--rrd-path', '-r', action='store', dest='rrd-path',
            default=settings.RRD_DIR, help="Path to search for RRD files. "\
                    "Default: %s" % settings.RRD_DIR),
        make_option('--minutes', '-m', action='store', dest='minutes',
            default=0, help="How many minutes to draw. If it is not "\
                    "indicated or 0 then nothing is done."),
        make_option('--daily', '-d', action='store_true', dest='daily',
            default=False, help='Makes daily graphs. Default: `False`.'),
        make_option('--weekly', '-w', action='store_true', dest='weekly',
            default=False, help='Makes weekly graphs. Default: `False`.'),
        make_option('--monthly', '-o', action='store_true', dest='monthly',
            default=False, help='Dumps monthly graphs. Default: `False`.'),
        make_option('--yearly', '-y', action='store_true', dest='yearly',
            default=False, help='Dumps yearly graphs. Default: `False`.'),
    )

    help = ""
    workers = []
    cache = BasicCache()

    def filter_rrds(self, path):
        rrds = []
        for base, ds, fs in os.walk(path):
            for f in fs:
                if f.endswith('.rrd'):
                    rrds.append(os.path.join(base, f))
        return rrds                    

    def deduce(self, rrd):
        f = os.path.basename(rrd)
        return {"server": int(f[1]), "variable": int(f[3]), "file": f, }

    def ts_days(self, days=1):
        """TODO: add some docstring for ts_days"""
        return int(time.time() - self.ts_minutes(60 * 24) * days)

    def ts_minutes(self, minutes=1):
        return int(time.time() - 60 * minutes)
        

    def handle(self, *args, **options):
        """
        """
        logger.info("** Collector graphics started **")

        periods = {
                'minutes': options['minutes'],
                'daily': 1 * DAY_MINUTES, 
                'weekly': 7 * DAY_MINUTES, 
                'monthly': 30 * DAY_MINUTES,
                'yearly': 365 * DAY_MINUTES,
                }
        if not any([options[p] for p in periods]):
            logger.error("Must indicate a period; see `[command] --help`"\
                    " for a list of options.")
            exit(MISSING_PARAMETERS_ERROR)

        rrds = self.filter_rrds(options['rrd-path'])

        for f_rrd in rrds:
            logger.debug("Processing %s" % f_rrd)
            try:
                info = self.deduce(f_rrd)
            except:
                logger.warn("Invalid RRD filename for '%s'" % f_rrd)
                continue

            v = self.cache.get(Variable, info["variable"])
            rrd = rrdtool.RRD(f_rrd)
            params = {
                    'format': 'AREA',
                    'variable': v.name,
                    'img': os.path.join(options['img-path'], info['file']),
                    'color': '0000FF',
                    }
            
            try:
                for p in periods:
                    if options[p]:
                        params['start'] = self.ts_minutes(periods[p])
                        params['img'] = "%s-%s.png" % (params['img'], p)
                        logger.info("Image for %s period in %s" % (p,
                            params['img']))
                        rrd.graph(**params)
            except:
                logger.exception("Exception generating graphics:")
        logger.info("** Collector graphics finished **")
        exit(SUCCESS)
