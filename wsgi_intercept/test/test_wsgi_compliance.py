import warnings
from wsgi_intercept import testing
from wsgi_intercept.testing import unittest
from wsgi_intercept.test import base

try:
    import httplib2
    has_httplib2 = True
except ImportError:
    has_httplib2 = False
_httplib2_skip_message = "httplib2 is not installed"
try:
    from paste import lint
    has_paste = True
except ImportError:
    has_paste = False
_paste_skip_message = "Paste is not installed"


@unittest.skipUnless(has_httplib2, _httplib2_skip_message)
@unittest.skipUnless(has_paste, _paste_skip_message)
class BaseComplianceCase(base.BaseTestCase):
    port = 80

    def setUp(self):
        super(BaseComplianceCase, self).setUp()
        warnings.simplefilter("error")
        self.addCleanup(warnings.resetwarnings)
        # Intercept httplib2 requests
        from wsgi_intercept.httplib2_intercept import install, uninstall
        install()
        self.addCleanup(uninstall)

    @property
    def wsgi_app(self):
        # Set up a prudent WSGI application 
        return lambda: lint.middleware(testing.create_fn())

    def make_one(self, *args):
        from httplib2 import Http
        return Http(*args)


class ComplianceTestCase(BaseComplianceCase):

    def test_success(self):
        http = self.make_one()
        resp, content = http.request(self.url, 'GET')
        self.assertTrue(testing.success())


class QuotingComplianceTestCase(BaseComplianceCase):
    # See issue 11
    # https://github.com/pumazi/wsgi_intercept2/issues/11

    def setUp(self):
        super(QuotingComplianceTestCase, self).setUp()
        self.inspected_env = {}

    @property
    def wsgi_app(self):
        def make_path_checking_app():
            def path_checking_app(environ, start_response):
                self.inspected_env['QUERY_STRING'] = environ['QUERY_STRING']
                self.inspected_env['PATH_INFO'] = environ['PATH_INFO']
                status = '200 OK'
                response_headers = [('Content-type','text/plain')]
                start_response(status, response_headers)
                return []
            return path_checking_app
        # Reassign the WSGI application
        return make_path_checking_app

    def test_quoting_issue11(self):
        http = self.make_one()
        url = self.url + 'spaced+words.html?word=something%20spaced'
        resp, content = http.request(url, 'GET')
        
        self.assertTrue('QUERY_STRING' in self.inspected_env,
                        "path_checking_app() was never called?")
        self.assertTrue('PATH_INFO' in self.inspected_env,
                        "path_checking_app() was never called?")
        self.assertEqual(self.inspected_env['PATH_INFO'],
                         '/spaced+words.html')
        self.assertEqual(self.inspected_env['QUERY_STRING'],
                         'word=something%20spaced')
