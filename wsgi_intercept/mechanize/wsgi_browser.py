"""
A mechanize browser that redirects specified HTTP connections to a WSGI
object.
"""

from httplib import HTTP
from mechanize import Browser as MechanizeBrowser
from wsgi_intercept.urllib2.wsgi_urllib2 import install_opener, uninstall_opener
try:
    from mechanize import HTTPHandler
except ImportError:
    # pre mechanize 0.1.0 it was a separate package
    # (this will break if it is combined with a newer mechanize)
    from ClientCookie import HTTPHandler

import sys, os.path
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
        install(self)
        MechanizeBrowser.__init__(self, *args, **kwargs)

_saved_UserAgent_http = None
def install(browser):
    global _saved_UserAgent
    # this is for some old version?
    browser.handler_classes['http'] = WSGI_HTTPHandler
    # for 0.0.11a
    install_opener()
    import mechanize
    _saved_UserAgent_http = mechanize.UserAgent.handler_classes['http']
    mechanize.UserAgent.handler_classes['http'] = WSGI_HTTPHandler
#     
# def uninstall():
#     if _saved_UserAgent_http is not None:
#         import mechanize._mechanize
#         mechanize._mechanize.UserAgent.handler_classes['http'] = _saved_UserAgent_http
#     uninstall_opener()