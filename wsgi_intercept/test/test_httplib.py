#! /usr/bin/env python2.4
from nose.tools import with_setup, raises, eq_
from wsgi_intercept import httplib_intercept
from socket import gaierror
import wsgi_intercept
from wsgi_intercept import test_wsgi_app
import httplib

_saved_debuglevel = None


def http_install():
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    httplib_intercept.install()
    wsgi_intercept.add_wsgi_intercept('http://some_hopefully_nonexistant_domain', 80, test_wsgi_app.create_fn)

def http_uninstall():
    wsgi_intercept.debuglevel = _saved_debuglevel
    wsgi_intercept.remove_wsgi_intercept('http://some_hopefully_nonexistant_domain', 80)
    httplib_intercept.uninstall()

@with_setup(http_install, http_uninstall)
def test_success():
    http = httplib.HTTPConnection('http://some_hopefully_nonexistant_domain:80')
    content = http.request('GET', '/').read()
    eq_(content, "WSGI intercept successful!\n")
    assert test_wsgi_app.success()



def https_install():
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    httplib_intercept.install()
    wsgi_intercept.add_wsgi_intercept('https://some_hopefully_nonexistant_domain', 443, test_wsgi_app.create_fn)

def https_uninstall():
    wsgi_intercept.debuglevel = _saved_debuglevel
    wsgi_intercept.remove_wsgi_intercept('https://some_hopefully_nonexistant_domain', 443)
    httplib_intercept.uninstall()
    
@with_setup(https_install, https_install)
def test_https_success():
    http = httplib.HTTPSConnection('https://some_hopefully_nonexistant_domain:80')
    resp, content = http.request('/', 'GET').read()
    assert test_wsgi_app.success()