#! /usr/bin/env python
import sys
import wsgi_intercept
from wsgi_intercept.urllib2 import wsgi_urllib2
from wsgi_intercept import test_wsgi_app, webtest

class WSGI_Test(webtest.WebCase):
    HTTP_CONN = wsgi_intercept.WSGI_HTTPConnection

    def setUp(self):
        wsgi_intercept.add_wsgi_intercept(self.HOST, self.PORT,
                                          test_wsgi_app.create_fn)

    def test_page(self):
        self.getPage('http://%s:%s/' % (self.HOST, self.PORT))
        assert test_wsgi_app.success()

if __name__ == '__main__':
    webtest.main()
