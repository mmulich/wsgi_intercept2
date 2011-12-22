from urllib2 import URLError
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest
from wsgi_intercept.test import base

try:
    import mechanize
    has_mechanize = True
except ImportError:
    has_mechanize = False
_skip_message = "mechanize is not installed"


@unittest.skipUnless(has_mechanize, _skip_message)
class MechanizeHttpTestCase(base.BaseTestCase):
    port = 80

    def make_one(self, *args):
        from mechanize import Browser
        return Browser(*args)

    def test_intercepted(self):
        b = self.make_one()
        b.open(self.url)
        self.assertTrue(testing.success())

    def test_intercept_removed():
        remove_intercept()
        b = self.make_one()
        with self.assertRaises(URLError):
            b.open(self.url)


@unittest.skipUnless(has_mechanize, _skip_message)
class MechanizeHttpsTestCase(MechanizeHttpTestCase):
    port = 443
