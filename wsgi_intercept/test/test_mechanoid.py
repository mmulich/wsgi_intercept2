#! /usr/bin/env python2.3
from wsgi_intercept.mechanoid_intercept import Browser
import wsgi_intercept
from wsgi_intercept import test_wsgi_app

###

_saved_debuglevel = None

def setup():
    _saved_debuglevel, wsgi_intercept.debuglevel = wsgi_intercept.debuglevel, 1
    wsgi_intercept.add_wsgi_intercept('some_hopefully_nonexistant_domain', 80, test_wsgi_app.create_fn)

def test():
    b = Browser()
    b.open('http://some_hopefully_nonexistant_domain:80/')
    assert test_wsgi_app.success()

def teardown():
    wsgi_intercept.debuglevel = _saved_debuglevel

if __name__ == '__main__':
    try:
        setup()
        test()
    finally:
        teardown()
        
    
    
