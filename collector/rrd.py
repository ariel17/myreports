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


import os
from time import time


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

    def create_rrd(self, interval, data_sources, start=None):
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
        interval_mins = float(interval) / 60
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
        cmd_create = ' '.join((
            'rrdtool create ', self.rrd_name, '--start %s' % str(start) if start
            else '', '--step', interval, ds_string,
            'RRA:AVERAGE:0.5:1:%s' % str(int(4000 / interval_mins)),
            'RRA:AVERAGE:0.5:%s:800' % str(int(30 / interval_mins)),
            'RRA:AVERAGE:0.5:%s:800' % str(int(120 / interval_mins)),
            'RRA:AVERAGE:0.5:%s:800' % str(int(1440 / interval_mins)),
            ))
        print cmd_create

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
        print cmd_update
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

        @img: Path to resulting image.
        @start: Timestamp begining.
        @end: Timestamp end.
        @variable: Variable name to draw.
        @color: Hexadecimal format.

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

        if 'end' not in p:
            p['end'] = int(time())

        args = "%(img)s --start %(start)s --end %(end)s "\
                "--vertical-label %(variable)s "\
                "DEF:v_%(variable)s=%(rrd_name)s:%(variable)s:AVERAGE "\
                "LINE2:v_%(variable)s#%(color)s" % p
        print "rrdtool graph " + args

        cmd = os.popen4("rrdtool graph " + args)
        cmd_output = cmd[1].read()

        if len(cmd_output) > 0:
            raise RRDException("Unable to build graphs: " + cmd_output)


class RRDException(Exception):
    pass
