from wsgi_intercept import testing
from wsgi_intercept.testing import unittest


class BaseTestCase(unittest.TestCase):
    port = 80
    domain = 'some_hopefully_nonexistant_domain'

    def setUp(self):
        import wsgi_intercept
        wsgi_intercept.add_wsgi_intercept(self.domain, self.port,
                                          testing.create_fn)
        self.addCleanup(wsgi_intercept.remove_wsgi_intercept,
                        self.domain, self.port)

    def make_one(self, *args):
        raise NotImplementedError

    @property
    def url(self):
        scheme = self.port == 80 and 'http' or 'https'
        return "%s://%s:%s/" % (scheme, self.domain, self.port)
