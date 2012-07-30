#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Django settings for myreports project.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"

import os

from logging.handlers import SysLogHandler


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
        # 'oracle'.
        'ENGINE': 'django.db.backends.',
        'NAME': '',      # Or path to database file if using sqlite3.
        'USER': '',      # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

DATETIME_FORMAT = "Y-m-d H:i:s"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "static/"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x6d$&^kwa4y9vs%eb&u^g-o-e*i-2kkj6zf&%6c3u_x_j!u#sk'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    # project apps:
    'server',
    'report',
    'collector',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s MyReports %(levelname)s %(module)s '\
                'PID#%(process)d %(message)s'
        },
        'daemon': {
            'format': '%(asctime)s MyReports %(levelname)s %(module)s '\
                'PID#%(process)d %(threadName)s %(message)s'
        },
        'simple': {
            'format': 'MyReports %(levelname)s %(message)s'
        },
        'full': {
            'format': 'MyReports %(levelname)s %(module)s PID#%(process)d '\
                '%(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': LOG_LEVEL,
            'class': 'django.utils.log.NullHandler',
            'formatter': 'verbose',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'syslog': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'full',
            'facility': SysLogHandler.LOG_LOCAL2,
        },
        'daemon': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'daemon',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['syslog', 'console', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'collector': {
            'handlers': ['daemon', 'mail_admins', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'myreports.collector.models': {
            'handlers': ['daemon', 'mail_admins', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'server': {
            'handlers': ['mail_admins', 'console', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'report': {
            'handlers': ['mail_admins', 'console', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'history': {
            'handlers': ['mail_admins', 'console', ],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

CACHES = {
    'default': {
        # File system cache based
        # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # 'LOCATION': os.path.join(PROJECT_ROOT, 'cache'),
        
        # In Memory based cache
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'LOCATION': 'myreports' # Name this instance it if you like.

        'TIMEOUT': 60 * 60 * 6,  # seconds
    }
}

COLLECTOR_CONF = {
    'host': '127.0.0.1',
    'port': 8000,
    'pidlock_timeout': 3,  # seconds
    'query_workers': 10,
    'query_time-lapse': 60  # seconds
}

RRD_DIR = os.path.join(PROJECT_ROOT, 'rrd')

COLLECTOR_APP_DIR = os.path.join(PROJECT_ROOT, 'collector')

GRAPH_DIR = os.path.join(STATIC_ROOT if STATIC_ROOT else \
        os.path.join(COLLECTOR_APP_DIR, 'static'), 'graph')

CRONTAB_TIME_LAPSE = 60  # seconds

if DEBUG:
    try:
        from settings_devel import *
    except:
        pass
