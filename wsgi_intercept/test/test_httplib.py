import httplib
import wsgi_intercept
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest


class HttpTestCase(unittest.TestCase):
    port = 80

    @property
    def connection_cls(self):
        return httplib.HTTPConnection

    def setUp(self):
        # Install the intercept
        from wsgi_intercept import httplib_intercept
        httplib_intercept.install()
        # Add the intercept for a nonexistant domain
        self.domain = 'some_hopefully_nonexistant_domain'
        wsgi_intercept.add_wsgi_intercept(self.domain, self.port,
                                          testing.create_fn)
        self.addCleanup(wsgi_intercept.remove_wsgi_intercept,
                        self.domain, self.port)
        # Cleanup with an intercept uninstall
        self.addCleanup(httplib_intercept.uninstall)

    def test_success(self):
        http = self.connection_cls(self.domain)
        http.request('GET', '/')
        content = http.getresponse().read()
        self.assertEqual(content, 'WSGI intercept successful!\n')
        self.assertTrue(testing.success())


class HttpsTestCase(HttpTestCase):
    port = 443

    @property
    def connection_cls(self):
        return httplib.HTTPSConnection
