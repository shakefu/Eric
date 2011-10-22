from setuptools import setup

setup(
        name='eric',
        version='0.0.2',
        description='Eric WSGI Framework',
        author='Jake Alheid',
        author_email='jacob.alheid@gmail.com',
        url='http://about.me/jake/',
        packages=['eric'],
        requires=[
            'nose>=1.1.2',
            ]
)

