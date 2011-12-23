from wsgi_intercept import testing
from wsgi_intercept.testing import unittest


class BaseTestCase(unittest.TestCase):
    port = 80
    domain = 'some_hopefully_nonexistant_domain'

    def setUp(self):
        import wsgi_intercept
        wsgi_intercept.add_wsgi_intercept(self.domain, self.port,
                                          self.wsgi_app)
        self.addCleanup(wsgi_intercept.remove_wsgi_intercept,
                        self.domain, self.port)

    @property
    def wsgi_app(self):
        return testing.create_fn

    def make_one(self, *args):
        raise NotImplementedError

    @property
    def url(self):
        scheme = self.port == 80 and 'http' or 'https'
        return "%s://%s:%s/" % (scheme, self.domain, self.port)


class BaseHttplib2TestCase(BaseTestCase):

    def setUp(self):
        super(BaseHttplib2TestCase, self).setUp()
        from wsgi_intercept.httplib2_intercept import install, uninstall
        install()
        self.addCleanup(uninstall)

    def make_one(self, *args):
        from httplib2 import Http
        return Http(*args)

    def test_success(self):
        http = self.make_one()
        resp, content = http.request(self.url, 'GET')
        self.assertEqual(content, "WSGI intercept successful!\n")
        self.assertTrue(testing.success())

