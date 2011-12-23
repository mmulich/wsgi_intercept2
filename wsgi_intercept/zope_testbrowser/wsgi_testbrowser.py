"""
A zope.testbrowser-style Web browser interface that redirects specified
connections to a WSGI application.
"""
import zope.testbrowser.browser
from zope.testbrowser.browser import Browser as ZopeTestbrowser
from wsgi_intercept.mechanize_intercept import Browser as InterceptBrowser
from wsgi_intercept.mechanize_intercept import install as mechanize_install
from wsgi_intercept.mechanize_intercept import uninstall as mechanize_uninstall


class Browser(ZopeTestbrowser):
    """
    Override the zope.testbrowser.browser.Browser interface so that it
    uses PatchedMechanizeBrowser 
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['mech_browser'] = InterceptBrowser()
        ZopeTestbrowser.__init__(self, *args, **kwargs)


def install():
    mechanize_install()
    zope.testbrowser.browser.Browser = Browser

def uninstall():
    mechanize_uninstall()
    zope.testbrowser.browser.Browser = ZopeTestbrowser
