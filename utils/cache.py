#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Cache framework utils.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


import logging
from django.core.cache import cache


logger = logging.getLogger(__name__)


class CacheWrapper(object):
    """
    Wrapper class for Django cache framework.
    """

    def __init__(self, cache, prefix=''):
        super(CacheWrapper, self).__init__()
        self.__cache = cache
        self.__prefix = prefix
        self.name = self.__class__.__name__

    def __get_key(self, key):
        """
        Formats properly the key for this command in the cache framework.
        """
        return "%s%s" % (self.__prefix, key)

    def get(self, key, default, cl=None, **query):
        """
        Obteins the value for the key indicated. If class is indicated in
        parameter 'cl', then it searches in models using the parameters
        indicated for kwargs named.
        """
        k = self.__get_key(key)
        v = self.__cache.get(k, None)
        if v != None:
            logger.debug("[%s] Found '%s'=%s" % (self.name, k, v))
            return v
        if not cl:
            logger.debug("[%s] Not found. Returning default: '%s'=%s" %
                    (self.name, k, repr(default)))
            return default
        logger.debug("[%s] Querying class %s, q=%s" %
                (self.name, cl.__name__, repr(query)))
        v = cl.objects.get(**query)
        self.set(k, v)
        return v

    def set(self, key, value):
        """
        Stores the key properly formatted with its value in the cache
        framework.
        """
        k = self.__get_key(key)
        self.__cache.set(k, value)
        logger.debug("[%s] Stored '%s'=%s" % (self.name, k, value))

    def do(self):
        """
        Returns the wrappered cache object to 'do' its own methods.
        """
        return self.__cache

    def get_list(self, list_ids_key, obj_key, obj_class, method, **query):
        """
        """
        ids = self.__cache.get(list_ids_key, [])
        logger.debug("[%s] List ids: '%s'=%s" % (self.name, list_ids_key,
            repr(ids)))

        if ids:
            objs = [self.get(obj_key % id, None, obj_class, id=id) \
                    for id in ids]
        else:
            logger.debug("[%s] Updating ids list cache: method=%s, query=%s" %
                    (self.name, method, repr(query)))
            objs = method(**query)
            [self.__cache.set(obj_key % o.id, o) \
                    for o in objs]
            self.__cache.set(list_ids_key, [o.id for o in objs])

        logger.debug("[%s] Query result: %s=%s" % (self.name, list_ids_key,
            repr(objs)))
        return objs
