"""
A mechanize browser that redirects specified HTTP connections to a WSGI
object.
"""
from http.client import HTTP
import mechanize
from mechanize import Browser as MechanizeBrowser
from wsgi_intercept.urllib2_intercept import install_opener, uninstall_opener
try:
    from mechanize import HTTPHandler
except ImportError:
    # pre mechanize 0.1.0 it was a separate package
    # (this will break if it is combined with a newer mechanize)
    from ClientCookie import HTTPHandler

from wsgi_intercept.urllib2_intercept import WSGI_HTTPHandler, WSGI_HTTPSHandler


class Browser(MechanizeBrowser):
    """
    A version of the mechanize browser class that
    installs the WSGI intercept handler
    """
    handler_classes = MechanizeBrowser.handler_classes.copy()
    handler_classes['http'] = WSGI_HTTPHandler
    handler_classes['https'] = WSGI_HTTPSHandler


def install():
    mechanize.Browser = Browser
    install_opener()

def uninstall():
    mechanize.Browser = MechanizeBrowser
    uninstall_opener()
