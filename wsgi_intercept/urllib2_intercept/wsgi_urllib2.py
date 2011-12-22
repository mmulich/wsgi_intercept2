import urllib2
from urllib2 import HTTPHandler, HTTPSHandler
from wsgi_intercept import WSGI_HTTPConnection, WSGI_HTTPSConnection


class WSGI_HTTPHandler(HTTPHandler):
    """
    Override the default HTTPHandler class with one that uses the
    WSGI_HTTPConnection class to open HTTP URLs.
    """

    def http_open(self, req):
        return self.do_open(WSGI_HTTPConnection, req)


class WSGI_HTTPSHandler(HTTPSHandler):
    """
    Override the default HTTPSHandler class with one that uses the
    WSGI_HTTPConnection class to open HTTPS URLs.
    """

    def https_open(self, req):
        return self.do_open(WSGI_HTTPSConnection, req)

    
def install_opener():
    handlers = [WSGI_HTTPHandler()]
    if WSGI_HTTPSHandler is not None:
        handlers.append(WSGI_HTTPSHandler())
    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)
    return opener

def uninstall_opener():
    urllib2.install_opener(None)
