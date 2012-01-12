import urllib.request, urllib.error, urllib.parse
from wsgi_intercept import testing
from wsgi_intercept.test import base


class Urllib2HttpTestCase(base.BaseTestCase):

    def setUp(self):
        super(Urllib2HttpTestCase, self).setUp()
        from wsgi_intercept.urllib2_intercept import install
        from wsgi_intercept.urllib2_intercept import uninstall
        install()
        self.addCleanup(uninstall)

    def test_success(self):
        urllib.request.urlopen(self.url)
        self.assertTrue(testing.success())

    def test_default_port(self):
        url = self.url
        url.replace(':%s' % self.port, '')
        urllib.request.urlopen(url)
        self.assertTrue(testing.success())


class Urllib2HttpsTestCase(Urllib2HttpTestCase):
    port = 443
