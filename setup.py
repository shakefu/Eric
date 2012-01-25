import setuptools
from distutils.core import setup

setup(
        name='eric',
        version='0.0.2',
        description='Eric WSGI Framework',
        author='Jake Alheid',
        author_email='jacob.alheid@gmail.com',
        url='http://about.me/jake/',
        packages=['eric'],
        install_requires=[
            'nose >= 1.1.2',
            'gevent >= 0.13.6',
            'tenjin >= 1.0.2',
            'webext >= 0.0.1',
            ]
)

