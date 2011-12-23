#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Fabric file to automate tasks.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from fabric.api import *
from fabric.colors import red, green
import os
import settings


CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))
IGNORE = os.path.join(CURRENT_DIR, ".gitignore")


def clean(all=False):
    """
    Use .gitignore rules to clean the current project.
    """
    fd = open(IGNORE, "r")
    for pattern in fd:
        if not all:  # only erase generic patterns, not specific files
            if "*" not in pattern:
                continue
        local("/usr/bin/find -name '%s' -delete" % pattern.strip())
    print green("Project cleaned.")            


def clean_startup():
    """
    Remove only those files that are the result of using this application, like
    log files, unremoved pid files.
    """
    for pattern in ('*.pyc', '*pyo', '*.pid*', '*.log', 'gabrielle-*',
            'natalie-*'):
        local("/usr/bin/find -name '%s' -delete" % pattern.strip())
    print green("Project cleaned.")            


def create_dirs():
    """
    TODO: add some docstring for check_directories
    """
    for d in [settings.GRAPH_DIR, settings.RRD_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            print "Created dir '%s'" % d
