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


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpTestCase(base.BaseHttplib2TestCase):
    port = 80

    @unittest.skipIf(*testing.funky_dns_resolution)
    def test_bogus_domain(self):
        from wsgi_intercept.httplib2_intercept import HTTP_WSGIInterceptorWithTimeout
        with self.assertRaises(gaierror):
            HTTP_WSGIInterceptorWithTimeout("_nonexistant_domain_").connect()


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpsTestCase(base.BaseHttplib2TestCase):
    port = 443
