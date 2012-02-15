"""
The Eric project.

"""
import importlib

import webob
import webob.exc


MIDDLEWARE = []


class BaseMiddleware(object):
    """ Base class for middleware. """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """ Called in wsgi execution. """
        request = webob.Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)


def import_object(obj):
    """ Imports a dot separated obj and returns the imported object.

        :param str obj: Object to import

    """
    if '.' in obj:
        module, obj = obj.rsplit('.', 1)
        module = importlib.import_module(module)
        obj = getattr(module, obj)
    else:
        obj = importlib.import_module(module)

    return obj


class Eric(object):
    """ Eric WSGI framework. """
    def __init__(self, middleware=MIDDLEWARE):
        app = webob.exc.HTTPNotFound
        for ware in middleware[1:]:
            ware = import_object(ware)
            app = ware(app)

        self.app = app

    def __call__(self, environ, start_response):
        request = webob.Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)


