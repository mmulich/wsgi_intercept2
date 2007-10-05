
from setuptools import setup, find_packages
setup(
    name = 'wsgi_intercept',
    version = "0.3",
    author = 'Titus Brown, Kumar McMillan',
    author_email = 'kumar.mcmillan@gmail.com',
    description = "in-process testing of WSGI applications",
    long_description = """\
This library lets you intercept calls to any specific host/port combination and redirect them into a WSGI application. Thus, you can avoid spawning multiple processes or threads to test your Web app. The interception works by subclassing httplib.HTTPConnection and installing it as a handler for 'http' requests; requests that aren't intercepted are passed on to the standard handler.
""",
    license = 'MIT License',
    download_url="",
    packages = find_packages(),
    test_suite = "nose.collector"
    )