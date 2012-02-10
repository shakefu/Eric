"""
WSGI Framework

"""
import re
import sys
import json
import pprint
import urlparse
import importlib
import functools
from collections import defaultdict

import webob
import webob.exc

import eric.render


LOAD_APPS = [
        'tmp.app',
        'eric.render',
        ]

WSGI_MIDDLEWARE = [
        # 'eric.wsgi.debug_env',
        'eric.wsgi.route',
        ]

WSGI_MIDDLEWARE_CACHE = []

ROUTES = defaultdict(list)


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
    request_method = environ['REQUEST_METHOD']

    response = None
    for regex, handler in ROUTES[request_method] + ROUTES[None]:
        if regex.match(path):
            response = handler(environ, start_response)
            break

    if response:
        return response

    return webob.exc.HTTPNotFound()(environ, start_response)


def register_route(method, pattern, handler):
    ROUTES[method].append((re.compile(pattern), handler))


class Handler(object):
    def __init__(self, pattern, method=None):
        self.pattern = pattern
        self.method = method

    @property
    def routes(self):
        return ROUTES

    @classmethod
    def GET(cls, pattern, *args, **kwargs):
        return cls(pattern, 'GET', *args, **kwargs)

    @classmethod
    def POST(cls, pattern, *args, **kwargs):
        return cls(pattern, 'POST', *args, **kwargs)

    def handle(self, environ, start_response):
        return self.func(environ, start_response)

    def __call__(self, func):
        self.func = func
        register_route(
                self.method,
                self.pattern,
                self.handle)

        return func


class RequestHandler(Handler):
    def handle(self, environ, start_response):
        req = webob.Request(environ)
        body = self.handle_request(req)
        if isinstance(body, (webob.exc.HTTPException, webob.Response)):
            return body(environ, start_response)
        return webob.Response(body)(environ, start_response)

    def handle_request(self, req):
        return self.func(req)


class TenjinHandler(RequestHandler):
    def __init__(self, pattern, method=None, template=None):
        super(TenjinHandler, self).__init__(pattern, method)
        self.template = template

    def __call__(self, func):
        super(TenjinHandler, self).__call__(func)
        if not self.template:
            self.template = ':' + self.func.func_name

    def handle_request(self, req):
        context = self.func(req)
        if isinstance(context, webob.exc.HTTPException):
            return context
        return eric.render.with_tenjin(context, self.template)


class JSONHandler(RequestHandler):
    def handle_request(self, req):
        response = self.func(req)
        return json.dumps(response)


