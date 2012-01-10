from urllib.error import URLError
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest
from wsgi_intercept.test import base

try:
    import zope.testbrowser
    has_zope_testbrowser = True
except ImportError:
    has_zope_testbrowser = False
_skip_message = "zope.testbrowser is not installed"


@unittest.skipUnless(has_zope_testbrowser, _skip_message)
class ZopeTestbrowserHttpTestCase(base.BaseTestCase):
    port = 80

    def setUp(self):
        super(ZopeTestbrowserHttpTestCase, self).setUp()
        from wsgi_intercept.zope_testbrowser import install, uninstall
        install()
        self.addCleanup(uninstall)

    def make_one(self, *args):
        from zope.testbrowser.browser import Browser
        return Browser(*args)

    def test_intercepted(self):
        b = self.make_one()
        b.open(self.url)
        self.assertTrue(testing.success())

    @unittest.skipIf(*testing.funky_dns_resolution)
    def test_intercept_removed(self):
        from wsgi_intercept import remove_wsgi_intercept
        remove_wsgi_intercept()
        b = self.make_one()
        with self.assertRaises(URLError):
            b.open(self.url)


@unittest.skipUnless(has_zope_testbrowser, _skip_message)
class ZopeTestbrowserHttpsTestCase(ZopeTestbrowserHttpTestCase):
    port = 443
