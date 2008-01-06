#! /usr/bin/env python2.4
import warnings
from wsgi_intercept.httplib2_intercept import install, uninstall
import wsgi_intercept
from wsgi_intercept import test_wsgi_app
import httplib2
from paste import lint

_saved_debuglevel = None

def prudent_wsgi_app():
    return lint.middleware(test_wsgi_app.create_fn())

def setup():
    warnings.simplefilter("error")
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    install()
    wsgi_intercept.add_wsgi_intercept('some_hopefully_nonexistant_domain', 80, prudent_wsgi_app)

def test():
    http = httplib2.Http()
    resp, content = http.request('http://some_hopefully_nonexistant_domain:80/', 'GET')
    assert test_wsgi_app.success()

def teardown():
    warnings.resetwarnings()
    wsgi_intercept.debuglevel = _saved_debuglevel
    uninstall()

if __name__ == '__main__':
    setup()
    try:
        test()
    finally:
        teardown()
