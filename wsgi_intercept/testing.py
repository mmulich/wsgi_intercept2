"""
A module to support this packages tests. The functionality found here can
also be used in packages that may depend on this one.

Contains
--------

- A simple WSGI application for testing.
- unittest2 indirection
"""
import os
import sys
import unittest


# Some tests will fail if your ISP or DNS provider resolves
#   all names. For example, Verizon resolves all names and in most
#   cases tries to redirect you to a web search page.
_value = os.environ.get('FUNKY_DNS_RESOLUTION', None)
has_funky_dns_resolution = _value is None and False or True
_dns_skip_message = "DNS resolves any given name. Therefore, the results of this test are invalid."
#: Usage would be something like: @unitest.skipIf(*testing.funky_dns_resolution)
funky_dns_resolution = (has_funky_dns_resolution, _dns_skip_message,)


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
    
    return [b'WSGI intercept successful!\n']

def create_fn():
    global _app_was_hit
    _app_was_hit = False
    return simple_app
