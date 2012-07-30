#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Dumps graphics from RRDTool for all sections into image files.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"

import collector.rrd as rrdtool
import logging
import os
import time

from collector.cache import CacheWrapper
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from optparse import make_option
from report.models import Section, Variable
from sys import exit


logger = logging.getLogger(__name__)

SUCCESS, MISSING_PARAMETERS_ERROR = range(2)

MINUTE_SECONDS = 60
HOUR_MINUTES = 60
DAY_HOURS = 24
DAY_MINUTES = HOUR_MINUTES * DAY_HOURS

WEEK_DAYS = 7
MONTH_DAYS = 30
YEAR_DAYS = 365


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
        make_option('--hourly', '-u', action='store_true', dest='hourly',
            default=False, help='Makes hourly graphs. Default: `False`.'),
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
    cache_w = CacheWrapper(cache)

    def filter_rrds(self, path):
        rrds = []
        for base, ds, fs in os.walk(path):
            for f in fs:
                if f.endswith('.rrd'):
                    rrds.append(os.path.join(base, f))
        return rrds

    def ts_days(self, days=1):
        """TODO: add some docstring for ts_days"""
        return int(time.time() - self.ts_minutes(HOUR_MINUTES * DAY_HOURS) * \
                days)

    def ts_minutes(self, minutes=1):
        return int(time.time() - MINUTE_SECONDS * minutes)

    def handle(self, *args, **options):
        """
        """
        logger.info("** Collector graphics started **")

        periods = {
                'minutes': float(options['minutes']),
                'hourly': HOUR_MINUTES,
                'daily': DAY_MINUTES,
                'weekly': WEEK_DAYS * DAY_MINUTES,
                'monthly': MONTH_DAYS * DAY_MINUTES,
                'yearly': YEAR_DAYS * DAY_MINUTES,
                }
        if not any([options[p] for p in periods]):
            logger.error("Must indicate a period; see `[command] --help`"\
                    " for a list of options.")
            exit(MISSING_PARAMETERS_ERROR)

        rrds = self.filter_rrds(options['rrd-path'])

        for f_rrd in rrds:
            logger.debug("Processing %s" % f_rrd)
            try:
                info = rrdtool.RRDWrapper.deduce_from_file(f_rrd)
            except:
                logger.exception("Exception parsing RRD filename:")
                logger.warn("Invalid RRD filename for '%s'" % f_rrd)
                continue

            se = self.cache_w.get('section_%d' % info["section_id"], None,
                    Section, id=info["section_id"])
            v = self.cache_w.get('variable_%d' % info["variable_id"], None,
                    Variable, id=info["variable_id"])
            rrd = rrdtool.RRD(f_rrd)
            img_path = os.path.join(options['img-path'], info['file'])
            params = {
                    'format': 'AREA',
                    'variable': v.name,
                    'color': '0000FF',
                    'limits': se.parse_threshold(),
                    }
            try:
                for p in periods:
                    if options[p]:
                        params['start'] = self.ts_minutes(periods[p])
                        params['title'] = p.capitalize()
                        params['img'] = "%s-%s.png" % (img_path, p)
                        logger.info("Image for %s period in %s" % (p,
                            params['img']))
                        rrd.graph(**params)
            except:
                logger.exception("Exception generating graphics:")
        logger.info("** Collector graphics finished **")
        exit(SUCCESS)
