"""
A module to support this packages tests. The functionality found here can
also be used in packages that may depend on this one.

Contains
--------

- A simple WSGI application for testing.
- unittest2 indirection
"""
import sys

if sys.version_info >= (2, 7) and not sys.version_info <= (3, 1):
    try:
        import unittest2 as unittest
    except ImportError:
        raise RuntimeError("Missing dependency: unittest2")
else:
    import unittest


_app_was_hit = False

def success():
    return _app_was_hit

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    return ['WSGI intercept successful!\n']

def create_fn():
    global _app_was_hit
    _app_was_hit = False
    return simple_app
