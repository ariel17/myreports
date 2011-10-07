#!/bin/bash
python manage.py collector_rpc --stdout=/tmp/collector_rpc-out.log --stderr=/tmp/collector_rpc-err.log --pidfile=/tmp/collector_rpc.pid --host 127.0.0.1 --port 8001
