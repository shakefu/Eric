"""
WSGI Framework

"""
import re
import sys
import pprint
import urlparse
import importlib
import functools

import webob
import webob.exc

import eric.render


LOAD_APPS = [
        'tmp.app',
        'eric.render',
        ]

WSGI_MIDDLEWARE = [
        'eric.wsgi.debug_env',
        'eric.wsgi.route',
        ]

WSGI_MIDDLEWARE_CACHE = []

ROUTES = []


def load_apps():
    if LOAD_APPS:
        while LOAD_APPS:
            app = LOAD_APPS.pop()
            sys.modules[app] = importlib.import_module(app)


def entry(environ, start_response):
    """ Entry point into WSGI glue. """
    load_apps()

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

    return webob.exc.HTTPServerError()(environ, start_response)


def debug_env(environ, start_response):
    pprint.pprint(environ)


def route(environ, start_response):
    if 'PATH_INFO' not in environ:
        environ['PATH_INFO'] = ''

    path = environ['PATH_INFO']
    path = path[1:] if path.startswith('/') else path

    response = None
    for regex, method, handler in ROUTES:
        if method and method != environ['REQUEST_METHOD']:
            continue
        if regex.match(path):
            response = handler(environ, start_response)
            break

    if response:
        return response

    return webob.exc.HTTPNotFound()(environ, start_response)


class request(object):
    def __init__(self, pattern, template=None, method=None,
            render=eric.render.with_tenjin):
        self.pattern = pattern
        self.template = template
        self.method = method
        self.render = render

    def __call__(self, func):
        if not self.template:
            self.template = func.func_name + '.pyhtml'

        self.func = func
        self.routes.append((re.compile(self.pattern), self.method, self.handle))

        return func

    def handle(self, environ, start_response):
        req = webob.Request(environ)
        context = self.func(req)
        body = self.render(context=context, template=self.template)
        return webob.Response(body)(environ, start_response)

    @property
    def routes(self):
        return ROUTES

    @classmethod
    def GET(cls, pattern, template=None):
        return cls(pattern, template, 'GET')

    @classmethod
    def POST(cls, pattern, template=None):
        return cls(pattern, template, 'POST')


def register_route(pattern, method, handler):
    request.routes.append(re.compile(pattern), method, handler)


