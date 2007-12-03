#! /usr/bin/env python
import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import urllib2

from wsgi_intercept import urllib2_intercept
import wsgi_intercept
from wsgi_intercept import test_wsgi_app

_saved_debuglevel = None

def setup():
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    wsgi_intercept.add_wsgi_intercept('some_hopefully_nonexistant_domain', 80, test_wsgi_app.create_fn)

def test():
    urllib2_intercept.install_opener()
    urllib2.urlopen('http://some_hopefully_nonexistant_domain:80/')
    assert test_wsgi_app.success()

def teardown():
    wsgi_intercept.debuglevel = _saved_debuglevel