#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Fabric file to automate tasks.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from fabric.api import *
from fabric.colors import red, green
import os


CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))
IGNORE = os.path.join(CURRENT_DIR, ".gitignore")


def clean(all=False):
    fd = open(IGNORE, "r")
    for pattern in fd:
        if not all:  # only erase generic patterns, not specific files
            if "*" not in pattern:
                continue
        local("/usr/bin/find -name '%s' -delete" % pattern.strip())
    print green("Project cleaned.")            
