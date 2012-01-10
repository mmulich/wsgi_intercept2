import http.client
import wsgi_intercept
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest
from wsgi_intercept.test import base


class HttpTestCase(base.BaseTestCase):
    port = 80

    def make_one(self, *args):
        return http.client.HTTPConnection(*args)

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
        http = self.make_one(self.domain)
        http.request('GET', '/')
        content = http.getresponse().read()
        self.assertEqual(content, 'WSGI intercept successful!\n')
        self.assertTrue(testing.success())


class HttpsTestCase(HttpTestCase):
    port = 443

    def make_one(self, *args):
        return http.client.HTTPSConnection(*args)
