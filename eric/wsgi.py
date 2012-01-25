"""
WSGI Framework

"""

import pprint
import urlparse
import importlib

import tmp.app


WSGI_MIDDLEWARE = [
        'eric.wsgi.formdecode',
        'eric.wsgi.debug_env',
        'eric.wsgi.route',
        ]

WSGI_MIDDLEWARE_CACHE = []


def entry(env, app):
    """ Entry point into WSGI glue. """
    if not WSGI_MIDDLEWARE_CACHE:
        for middleware in WSGI_MIDDLEWARE:
            module, middleware = middleware.rsplit('.', 1)
            module = importlib.import_module(module)
            middleware = getattr(module, middleware)
            WSGI_MIDDLEWARE_CACHE.append(middleware)

    # TODO: Wrap env in a dict-like object that doesn't allow overwriting of
    # existing keys

    for middleware in WSGI_MIDDLEWARE_CACHE:
        response = middleware(env, app)
        if response:
            return response

    app('500 Internal Server Error', [('Content-type', 'text/html')])
    return "500 Internal Server Error"


def debug_env(env, app):
    pprint.pprint(env)


def formdecode(env, app):
    # TODO: Assign these to variables that make more sense (e.g. not HTTP-methods)
    # Maybe "data" and "query"?
    env['GET'] = urlparse.parse_qs(env['QUERY_STRING'])
    env['POST'] = urlparse.parse_qs(env['wsgi.input'].read())


def route(env, app):
    if 'PATH_INFO' not in env:
        env['PATH_INFO'] = '/'

    app('200 OK', [('Content-type', 'text/html')])
    return tmp.app.render('test.pyhtml', {'title':'Test', 'items':xrange(2)})

    app('404 Not Found', [('Content-type', 'text/html')])
    return "404 Not Found"

