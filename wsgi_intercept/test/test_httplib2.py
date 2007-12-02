#! /usr/bin/env python2.4
from wsgi_intercept.httplib2_intercept import install, uninstall
import wsgi_intercept
from wsgi_intercept import test_wsgi_app
import httplib2

_saved_debuglevel = None


def setup():
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    install()
    wsgi_intercept.add_wsgi_intercept('some_hopefully_nonexistant_domain', 80, test_wsgi_app.create_fn)

def test():
    http = httplib2.Http()
    resp, content = http.request('http://some_hopefully_nonexistant_domain:80/', 'GET')
    assert test_wsgi_app.success()

def teardown():
    wsgi_intercept.debuglevel = _saved_debuglevel
    uninstall()

if __name__ == '__main__':
    setup()
    try:
        test()
    finally:
        teardown()
