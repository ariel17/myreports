#!/bin/bash
python manage.py collector --stdout=/tmp/collector-out.log --stderr=/tmp/collector-err.log --pidfile=/tmp/collector.pid --host 0.0.0.0 --port 8000
