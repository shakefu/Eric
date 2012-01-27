"""
WSGI Framework

"""
import pprint
import urlparse
import importlib

import webob
import webob.exc

import tmp.app


WSGI_MIDDLEWARE = [
        # 'eric.wsgi.debug_env',
        'eric.wsgi.route',
        ]

WSGI_MIDDLEWARE_CACHE = []


class WriteOnceDict(dict):
    """ Dict-like class that only allows setting of keys once. """
    def __setitem__(self, item, value):
        if item in self:
            raise KeyError("Key already exists")
        return dict.__setitem__(self, item, value)


def entry(environ, start_response):
    """ Entry point into WSGI glue. """
    if not WSGI_MIDDLEWARE_CACHE:
        for middleware in WSGI_MIDDLEWARE:
            module, middleware = middleware.rsplit('.', 1)
            module = importlib.import_module(module)
            middleware = getattr(module, middleware)
            WSGI_MIDDLEWARE_CACHE.append(middleware)

    for middleware in WSGI_MIDDLEWARE_CACHE:
        response = middleware(environ, start_response)
        if response:
            return response

    start_response('500 Internal Server Error', [('Content-type', 'text/html')])
    return "500 Internal Server Error"


def debug_env(environ, start_response):
    pprint.pprint(environ)


def route(environ, start_response):
    if 'PATH_INFO' not in environ:
        environ['PATH_INFO'] = '/'

    request = webob.Request(environ)
    try:
        response = tmp.app.view(request)
    except webob.exc.HTTPException, exc:
        response = exc
    else:
        response = webob.Response(response)(environ, start_response)

    return response

    # start_response('200 OK', [('Content-type', 'text/html')])
    # return tmp.app.render('test.pyhtml', {'title':'Test', 'items':xrange(2)})

    start_response('404 Not Found', [('Content-type', 'text/html')])
    return "404 Not Found"

