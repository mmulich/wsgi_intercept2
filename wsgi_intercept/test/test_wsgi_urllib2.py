import urllib2
from wsgi_intercept import testing
from wsgi_intercept.test import base


class Urllib2HttpTestCase(base.BaseTestCase):

    def setUp(self):
        super(Urllib2HttpTestCase, self).setUp()
        from wsgi_intercept.urllib2_intercept import install_opener
        from wsgi_intercept.urllib2_intercept import uninstall_opener
        install_opener()
        self.addCleanup(uninstall_opener)

    def test_success(self):
        urllib2.urlopen(self.url)
        self.assertTrue(testing.success())

    def test_default_port(self):
        url = self.url
        url.replace(':%s' % self.port, '')
        urllib2.urlopen(url)
        self.assertTrue(testing.success())


class Urllib2HttpsTestCase(Urllib2HttpTestCase):
    port = 443
