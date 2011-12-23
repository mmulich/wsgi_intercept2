import os
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

_value = os.environ.get('FUNKY_DNS_RESOLUTION', None)
has_funky_dns_resolution = _value is None and False or True
_isp_skip_message = "DNS resolves any given name. Therefore, the results of this test are invalid."


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpTestCase(base.BaseHttplib2TestCase):
    port = 80

    @unittest.skipIf(has_funky_dns_resolution, _isp_skip_message)
    def test_bogus_domain(self):
        from wsgi_intercept.httplib2_intercept import HTTP_WSGIInterceptorWithTimeout
        with self.assertRaises(gaierror):
            # NOTE This test will fail if your ISP or DNS provider resolves
            #   all names. For example, Verizon resolves all names and in most
            #   cases tries to redirect you to a web search page.
            #   See also the unittest skip message.
            HTTP_WSGIInterceptorWithTimeout("_nonexistant_domain_").connect()


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpsTestCase(base.BaseHttplib2TestCase):
    port = 443
