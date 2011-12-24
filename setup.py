import os
from setuptools import setup, find_packages

version = '1.0a1'
description = "installs a WSGI application in place of a real URI for testing"

here = os.path.dirname(__file__)
readme = os.path.join(here, "README.rst")
long_description = open(readme).read()

tests_require = [
    'nose',
    'Paste',
    'httplib2',
    'mechanize',
    'mechanoid',
    'WebTest',
    'zope.testbrowser',
    'webunit',
    ]
extras_require = {
    'test': tests_require,
    'httplib2': ['httplib2'],
    'zope.testbrowser': ['zope.testbrowser', 'mechanize>=0.1.7',],
    'webunit': ['webunit'],
    'webtest': ['WebTest'],  # conventionally extras are lowercase
    'mechanoid': ['mechanoid'],
    'paste': ['Paste'],
    }

setup(
    name='wsgi_intercept',
    version=version,
    author='Titus Brown, Kumar McMillan',
    author_email='kumar.mcmillan@gmail.com',
    description=description,
    url="http://code.google.com/p/wsgi-intercept/",
    long_description=long_description,
    license='MIT License',
    packages=find_packages(),
    extras_require=extras_require,
    test_suite="nose.collector",
    tests_require=tests_require,
    )
