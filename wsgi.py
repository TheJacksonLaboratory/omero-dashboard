#!/usr/bin/env python
"""WSGI config adding site packages and path."""
import sys
import site

site.addsitedir('/var/www/example_flask_plotly/dashboard/lib/python3.6/site-packages/')
site.addsitedir('/var/www/example_flask_plotly/dashboard/lib64/python3.6/site-packages/')

sys.path.insert(0, '/var/www/example_flask_plotly')

from app import app as application
