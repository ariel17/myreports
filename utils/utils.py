#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: TODO
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


def to_list_dict(rs, headers):
    """
    Converts a resultset, given by 'rs' to a list of dictionaries, using
    'headers' as ordered column names.
    """
    result = []
    for row in rs:
        d = {}
        for (pos, col_name) in enumerate(headers):
            d[col_name] = row[pos]
        result.append(d)
    return result
