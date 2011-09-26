#!/bin/bash
python manage.py collector --stdout=/tmp/collector-out.log --stderr=/tmp/collector-err.log --pidfile=/tmp/collector.pid
