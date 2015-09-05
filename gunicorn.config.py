"""Gunicorn WSGI server configuration."""

import os

workers = os.getenv('MAX_WORKERS', os.cpu_count())
threads = os.getenv('MAX_THREADS', 4)

pidfile = 'gunicorn.pid'

errorlog = '-'

reload = True
