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
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Server
from report.models import Variable

import collector.rrd as rrdtool


logger = logging.getLogger(__name__)


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
        return {"server": int(f[1]), "section": int(f[3]),
                "variable": int(f[5]), "img": "%s.png" % f, }

    def ts_days(self, day=1):
        """TODO: add some docstring for ts_days"""
        return int(time.time() - 60 * 60 * days)

    def ts_minutes(self, minutes=1):
        return int(time.time() - 60 * minutes)
        

    def handle(self, *args, **options):
        """
        """
        logger.info("** Dumping RRDTool graphics **")
        rrds = self.filter_rrds(options['rrd-path'])
        for f_rrd in rrds:
            logger.debug("Processing %s" % f_rrd)
            info = self.deduce(f_rrd)
            v = self.cache.get(Variable, info["variable"])
            rrd = rrdtool.RRD(f_rrd)
            try:
                if options['minutes']:
                    ts = self.ts_minutes(int(options['minutes']))
                    img_path = os.path.join(options['img-path'], info['img'])
                    rrd.graph(img=img_path, start=ts, variable=v.name,
                            color='0000FF')
                if options['daily']:
                    ts = self.ts_days()
                    rrd.graph(img=info["img"], start=ts, variable=v.name,
                            color='0000FF')
                if options['weekly']:
                    ts = self.ts_days(7)
                    rrd.graph(img=info["img"], start=ts, variable=v.name,
                            color='0000FF')
                if options['monthly']:
                    ts = self.ts_days(30)
                    rrdtool.graph(img=info["img"], start=ts, variable=v.name,
                            color='0000FF')
                if options['yearly']:
                    ts = self.ts_days(365)
                    rrdtool.graph(img=info["img"], start=ts, variable=v.name,
                            color='0000FF')
            except:
                logger.exception("Exception:")
        logger.info("** Finished **")
