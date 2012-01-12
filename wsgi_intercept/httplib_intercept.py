
"""intercept HTTP connections that use httplib

(see wsgi_intercept/__init__.py for examples)

"""

import http.client
import wsgi_intercept
import sys
# Import the classes individually so that we have a copy when uninstalling.
from http.client import HTTPConnection, HTTPSConnection


def install():
    http.client.HTTPConnection = wsgi_intercept.InterceptedHTTPConnection
    http.client.HTTPSConnection = wsgi_intercept.InterceptedHTTPSConnection

def uninstall():
    http.client.HTTPConnection = HTTPConnection
    http.client.HTTPSConnection = HTTPSConnection
