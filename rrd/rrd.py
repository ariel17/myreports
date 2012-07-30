#!/usr/bin/env python

#  Copyright (c) 2005, Corey Goldberg
#
#  RRD.py is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

"""

@author: Corey Goldberg
@copyright: (C) 2005 Corey Goldberg
@license: GNU General Public License (GPL)

Downloaded from http://www.goldb.org/rrdpython.html
"""


import logging
import os

from time import time


logger = logging.getLogger(__name__)

RRD_NAME_FORMAT = "s%(server_id)d-se%(section_id)d-v%(variable_id)d%(suffix)s"


class RRDException(Exception):
    pass


class TimeLapseException(Exception):
    """
    A time lapse exception.
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class RRD:
    """
    Data access layer that provides a wrapper for RRDtool.

    RRDtool is a data logging and graphing application. RRD (Round Robin
    Database) is a system to store and display time-series data. It stores the
    data in a very compact way that will not expand over time.

    @ivar rrd_name: Name (and path) of the RRD
    """

    def __init__(self, rrd_name):
        """
        @param rrd_name: Name (and path) of the RRD
        """
        self.rrd_name = rrd_name

    def create_rrd(self, interval, data_sources, start=None, averages=None):
        """
        Create a new RRD.

        If an RRD of the same name already exists, it will be replaced with the
        new one.

        @param interval: Interval in seconds that data will be fed into the RRD
        @param data_sources: Nested sequence (e.g. List of tuples) of data
            sources (DS) to store in the RRD.
            Each data source is passed in as: (name, type, min_value,
            max_value). If you try to update a data source with a value that
            is not within its accepted range, it will be ignored.
            min_value and max_value can be replaced with a 'U' to accept
            unlimited values.
        """
        interval = str(interval)
        # heartbeat defines the maximum number of seconds that may pass
        # between two updates of this data source before the value of the data
        # source is assumed to be *UNKNOWN*.
        heartbeat = str(int(interval) * 2)

        # unpack the tuples from the list and build the string of data sources
        # used to create the RRD
        ds_string = ''
        for ds_name, ds_type, ds_min, ds_max in data_sources:
            # ds_string = ''.join((ds_string, ' DS:', str(ds_name), ':',
            #   str(ds_type), ':', heartbeat, ':', str(ds_min), ':',
            #   str(ds_max)))
            ds_string += ':'.join((' DS', str(ds_name), str(ds_type),
                heartbeat, str(ds_min), str(ds_max)))

        # build the command line to send to RRDtool
        parts = ['rrdtool create ', self.rrd_name,
                '--start %s' % str(start) if start else '',
                '--step %s' % str(interval), ds_string, ]

        for a in (averages if averages else (('0.5', '1', '10'),)):
            parts.append('RRA:AVERAGE:%s:%s:%s' % (a[0], a[1], a[2]))

        cmd_create = ' '.join(parts)
        logger.debug("Executing: `%s`" % cmd_create)

        # execute the command as a subprocess and return file objects
        # (child_stdin, child_stdout_and_stderr)
        cmd = os.popen4(cmd_create)
        cmd_output = cmd[1].read()
        [fd.close() for fd in cmd]

        # check if anything comes back (the only output would be stderr)
        if len(cmd_output) > 0:
            raise RRDException("Unable to create RRD: " + cmd_output)

    def update(self, *values):
        """
        Update the RRD with a new set of values.

        Updates must supply a set of values that match the number of data
        sources (DS) containted in the RRD. (i.e. You can not update an RRD
        with 1 value when the RRD contains 2 DS's)
        @param values: Values to be inserted into the RRD (arbitrary number of
            scalar arguments)
        """
        # we need the values in a colon delimited list to add to our command
        # line so we take the list of values, convert them to strings and
        # append a colon to each, join the list into a string, and chop the
        # last character to remove the trailing colon values_args = ''.join(
        # [str(value) + ":" for value in values])[:-1]
        values_args = " ".join([':'.join((str(ts), str(v)))
            for (ts, v) in values])
        # build the command line to send to RRDtool
        # cmd_update = ''.join(('rrdtool update ', self.rrd_name, ' N:',)) +
        #   values_args
        cmd_update = "rrdtool update %s %s" % (self.rrd_name, values_args)
        logger.debug("Executing: `%s`" % cmd_update)

        # execute the command as a subprocess and return file objects
        # (child_stdin, child_stdout_and_stderr)
        cmd = os.popen4(cmd_update)
        cmd_output = cmd[1].read()
        [fd.close() for fd in cmd]
        # check if anything comes back (the only output would be stderr)
        if len(cmd_output) > 0:
            raise RRDException("Unable to update the RRD: " + cmd_output)

    def graph(self, **kwargs):
        """
        Build a graphic based on a rrd previously created.

        Parameters:
        ***********

        @title: Graph title.
        @img: Path to resulting image.
        @start: Timestamp begining.
        @end: Timestamp end.
        @variable: Variable name to draw.
        @color: Hexadecimal format.
        @limits: Limits to mark in graph, as RRDTool command parameters.


        Colors:
        *******

        red     #FF0000
        green   #00FF00
        blue    #0000FF
        magenta #FF00FF     (mixed red with blue)
        gray    #555555     (one third of all components)
        """

        p = {'rrd_name': self.rrd_name, }
        p.update(kwargs)
        p.setdefault('end', int(time()))

        args = "%(img)s --start %(start)s --end %(end)s "\
                "--vertical-label %(variable)s "\
                "--title %(title)s "\
                "DEF:v_%(variable)s=%(rrd_name)s:%(variable)s:AVERAGE "\
                "%(format)s:v_%(variable)s#%(color)s "\
                "%(limits)s" % p
        cmd_graph = "rrdtool graph " + args
        logger.debug("Executing: `%s`" % cmd_graph)

        cmd = os.popen4(cmd_graph)
        cmd_output = cmd[1].read()

        if len(cmd_output) > 0 and 'error' in cmd_output.lower():
            raise RRDException("Exception building graphs: " + cmd_output)
        else:
            logger.info("rrdtool output: %s" % cmd_output)


class RRDWrapper(object):
    """
    TODO: add some docstring for RRDWrapper
    """
    v_name = None
    rrd = None
    rrd_path = None
    last_update_path = None
    time_lapse = None
    rrd_dir = None

    def __init__(self, **kwargs):
        self.rrd_path = kwargs["rrd_path"]
        self.rrd = RRD(kwargs["rrd_path"])
        self.last_update_path = kwargs["last_update_path"]
        self.v_name = kwargs["v_name"]
        self.time_lapse = kwargs["time_lapse"]
        self.rrd_dir = kwargs["rrd_dir"]

        if kwargs.get("create", False) and \
                not os.path.exists(kwargs["rrd_path"]):
            self.create()

    @staticmethod
    def get_path(rrd_dir, server_id, section_id, variable_id, suffix='.rrd'):
        """
        """
        return os.path.join(rrd_dir, RRD_NAME_FORMAT % \
                {"server_id": server_id, "section_id": section_id,
                    "variable_id": variable_id, "suffix": suffix})

    @staticmethod
    def get_instance(server, section, variable, time_lapse, rrd_dir):
        """
        """
        rrd_path = RRDWrapper.get_path(rrd_dir, server.id, section.id,
                variable.id)
        last_update_path = RRDWrapper.get_path(rrd_dir, server.id, section.id,
                variable.id, '.last-update')
        return RRDWrapper(rrd_path=rrd_path, last_update_path=last_update_path,
                v_name=variable.name, time_lapse=time_lapse, rrd_dir=rrd_dir,
                create=True)

    @staticmethod
    def deduce_from_file(rrd):
        """
        Obtains info from file name.
        """
        def get_int(s):
            return ''.join([c for c in s if c in '0123456789'])

        f = os.path.basename(rrd)
        ff = f.split("-")
        return {"server_id": int(get_int(ff[0])),
                "section_id": int(get_int(ff[1])),
                "variable_id": int(get_int(ff[2])),
                "file": f, }

    def get_last_update(self):
        """
        """
        with open(self.last_update_path, 'r') as f:
            last_update_time = int(f.readline().strip())

        logger.debug("Last updated time in %s: %d" % (self.last_update_path,
            last_update_time))

        return last_update_time

    def set_last_update(self, timestamp):
        """
        """
        logger.debug("Updated time to %d in %s" % (timestamp, \
                self.last_update_path))

        with open(self.last_update_path, 'w') as f:
            f.write(str(timestamp).strip())

    def create(self, now=int(time())):
        """
        """
        now_start = now - self.time_lapse
        now_start -= now_start % 10  # fixed to fit rrd laps
        logger.info("Creating new RRD file in %s" % self.rrd_path)
        self.rrd.create_rrd(self.time_lapse,
                ((self.v_name, 'GAUGE', 'U', 'U'),),
                start=now_start)
        self.set_last_update(now_start)
        logger.debug("Setted initial time to %d" % now_start)

    def __must_update(self, last_update, now):
        """TODO: add some docstring for must_update"""
        diff = now - last_update
        return (False if diff < self.time_lapse else True, diff)

    def __fix_update_time(self, last_update, now):
        """
        Changes the timestamp to use as time mark for update. Since it doesn't
        now how many time had passed (maybe the server was down for a few hours
        or not) must determine the closer timestamp passed.

        Parameteres:
        @last_update (int): last timestamp saved.
        @now (int): actual timestamp obteined.

        Returns:
        Int: The closer timestamp mark to update.
        """
        factor = (now - last_update) / self.time_lapse
        return factor * self.time_lapse + last_update

    def update(self, value, now=int(time())):
        """
        """
        last_update = self.get_last_update()
        must_update, sec = self.__must_update(last_update, now)
        if not must_update:
            raise TimeLapseException("It isn't time to update: %d seconds "\
                    "(must at >= %d seconds)." % (sec, \
                    self.time_lapse))

        logger.debug("It is time to update :) %d seconds "\
                "(must at >=%d seconds)." % (sec, self.time_lapse))

        fv = int(float(value))
        logger.debug("Floored value: %s=%d" % (self.v_name, fv))

        fixed_time = self.__fix_update_time(last_update, now)
        logger.debug("Fixed time=%d" % fixed_time)

        self.rrd.update((fixed_time, fv),)

        self.set_last_update(fixed_time)
