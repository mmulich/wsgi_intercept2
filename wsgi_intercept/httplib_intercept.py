
"""intercept HTTP connections that use httplib

(see wsgi_intercept/__init__.py for examples)

"""

import http.client
import wsgi_intercept
import sys
# Import the classes individually so that we have a copy when uninstalling.
from http.client import HTTPConnection
try:
    from http.client import HTTPSConnection
    has_ssl_support = True
except ImportError:
    has_ssl_support = False


def install():
    http.client.HTTPConnection = wsgi_intercept.InterceptedHTTPConnection
    if has_ssl_support:
        http.client.HTTPSConnection = wsgi_intercept.InterceptedHTTPSConnection

def uninstall():
    http.client.HTTPConnection = HTTPConnection
    if has_ssl_support:
        http.client.HTTPSConnection = HTTPSConnection
