from socket import gaierror
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest
from wsgi_intercept.test import base
try:
    import httplib2
    has_httplib2 = True
except ImportError:
    has_httplib2 = False
_skip_message = "httplib2 is not installed"


class Httplib2BaseMixin:
    port = 0

    def make_one(self, *args):
        from httplib2 import Http
        return Http(*args)

    def test_success(self):
        http = self.make_one()
        resp, content = http.request(self.url, 'GET')
        self.assertEqual(content, "WSGI intercept successful!\n")
        self.assertTrue(test_wsgi_app.success())


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpTestCase(Httplib2BaseMixin, base.BaseTestCase):
    port = 80

    def test_bogus_domain(self):
        from wsgi_intercept.httplib2_intercept import HTTP_WSGIInterceptorWithTimeout
        with self.assertRaises(gaierror):
            HTTP_WSGIInterceptorWithTimeout("_nonexistant_domain_").connect()


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpsTestCase(Httplib2BaseMixin, base.BaseTestCase):
    port = 443
