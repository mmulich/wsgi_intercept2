"""
A mechanize browser that redirects specified HTTP connections to a WSGI
object.
"""

from httplib import HTTP
from mechanize import Browser as MechanizeBrowser
try:
    from mechanize import HTTPHandler
except ImportError:
    # pre mechanize 0.1.0 it was a separate package
    # (this will break if it is combined with a newer mechanize)
    from ClientCookie import HTTPHandler

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from wsgi_intercept import WSGI_HTTPConnection

class WSGI_HTTPHandler(HTTPHandler):
    def http_open(self, req):
        return self.do_open(WSGI_HTTPConnection, req)

class Browser(MechanizeBrowser):
    """
    A version of the mechanize browser class that
    installs the WSGI intercept handler
    """
    def __init__(self, *args, **kwargs):
        # install WSGI intercept handler.
        self.handler_classes['http'] = WSGI_HTTPHandler
        MechanizeBrowser.__init__(self, *args, **kwargs)
