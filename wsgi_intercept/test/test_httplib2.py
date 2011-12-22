from socket import gaierror
import wsgi_intercept
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest

try:
    import httplib2
    has_httplib2 = True
except ImportError:
    has_httplib2 = False
_skip_message = "httplib2 is not installed"


class Httplib2BaseMixin:
    port = 0

    @property
    def connection_cls(self):
        from httplib2 import Http
        return Http

    def setUp(self):
        # Install the intercept
        from wsgi_intercept import httplib2_intercept
        httplib2_intercept.install()
        # Add the intercept for a nonexistant domain
        self.domain = 'some_hopefully_nonexistant_domain'
        wsgi_intercept.add_wsgi_intercept(self.domain, self.port,
                                          testing.create_fn)
        self.addCleanup(wsgi_intercept.remove_wsgi_intercept,
                        self.domain, self.port)
        # Cleanup with an intercept uninstall
        self.addCleanup(httplib2_intercept.uninstall)

    def test_success(self):
        http = self.connection_cls()
        url = 'http://%s:%s/' % (self.domain, self.port)
        resp, content = http.request(url, 'GET')
        self.assertEqual(content, "WSGI intercept successful!\n")
        self.assertTrue(test_wsgi_app.success())


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpTestCase(Httplib2BaseMixin, unittest.TestCase):
    port = 80

    def test_bogus_domain(self):
        wsgi_intercept.debuglevel = 1;
        from wsgi_intercept.httplib2_intercept import HTTP_WSGIInterceptorWithTimeout
        with self.assertRaises(gaierror):
            HTTP_WSGIInterceptorWithTimeout("_nonexistant_domain_").connect()


@unittest.skipUnless(has_httplib2, _skip_message)
class Httplib2HttpsTestCase(Httplib2BaseMixin, unittest.TestCase):
    port = 443
