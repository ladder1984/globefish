#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import mimetypes
import os
import sys
import traceback
import re
import Cookie
import threading
import time

from globefish.router.common import Router
from globefish.server.common import BaseServer
from globefish.server.wsgiref_adaptor import WSGIRefServer

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs


# 异常
######################################################################################################
class GlobefishException(Exception):
    pass



class HTTPError(GlobefishException):
    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)

    def __str__(self):
        return self.output


class BreakTheGlobefish(GlobefishException):
    def __init__(self, output):
        self.output = output


# WSGI抽象
######################################################################################################
def WSGIHandler(environ, start_response):
    """ WSGI-handler ."""
    global request
    global response
    request.bind(environ)
    response.bind()
    try:
        handler, args = Router.match_url(request.path, request.method)
        if not handler:
            raise HTTPError(404, "Not found")
        output = handler(**args)
    except BreakTheGlobefish as e:
        output = e.output
    except Exception as e:
        response.status = getattr(e, 'http_status', 500)
        errorhandler = ERROR_HANDLER.get(response.status, error_default)
        try:
            output = errorhandler(e)
        except:
            output = "Exception within error handler!"
        if response.status == 500:
            request._environ['wsgi.errors'].write("Error (500) on '%s': %s\n" % (request.path, e))

    for c in response.COOKIES.values():
        response.header.add('Set-Cookie', c.OutputString())
    status = '%d %s' % (response.status, HTTP_CODES[response.status])
    start_response(status, list(response.header.items()))

    if hasattr(output, 'read'):
        fileoutput = output
        if 'wsgi.file_wrapper' in environ:
            return environ['wsgi.file_wrapper'](output)
        else:
            return iter(lambda: fileoutput.read(8192), '')
    elif isinstance(output, str):
        return [output]
    else:
        return output


class Request(threading.local):
    "清除老数据并创建一个新的Response对象 "

    def bind(self, environ):
        """ 绑定当前环境到request对象 """
        self._environ = environ
        self._GET = None
        self._POST = None
        self._PUT = None
        self._DELETE = None
        self._GETPOST = None
        self._COOKIES = None
        self.path = self._environ.get('PATH_INFO', '/').strip()
        if not self.path.startswith('/'):
            self.path = '/' + self.path

    @property
    def method(self):

        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def query_string(self):

        return self._environ.get('QUERY_STRING', '')

    @property
    def input_length(self):

        try:
            return int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            return 0

    @property
    def GET(self):

        if self._GET is None:
            raw_dict = parse_qs(self.query_string, keep_blank_values=1)
            self._GET = {}
            for key, value in raw_dict.items():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):

        if self._POST is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._POST = {}
            if raw_data:
                for key in raw_data:
                    if isinstance(raw_data[key], list):
                        self._POST[key] = [v.value for v in raw_data[key]]
                    elif raw_data[key].filename:
                        self._POST[key] = raw_data[key]
                    else:
                        self._POST[key] = raw_data[key].value
        return self._POST

    @property
    def PUT(self):
        if self._PUT is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._PUT = {}
            if raw_data:
                for key in raw_data:
                    if isinstance(raw_data[key], list):
                        self._PUT[key] = [v.value for v in raw_data[key]]
                    elif raw_data[key].filename:
                        self._PUT[key] = raw_data[key]
                    else:
                        self._PUT[key] = raw_data[key].value
        return self._PUT

    @property
    def DELETE(self):
        if self._DELETE is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._DELETE = {}
            if raw_data:
                for key in raw_data:
                    if isinstance(raw_data[key], list):
                        self._DELETE[key] = [v.value for v in raw_data[key]]
                    elif raw_data[key].filename:
                        self._DELETE[key] = raw_data[key]
                    else:
                        self._DELETE[key] = raw_data[key].value
        return self._DELETE

    # @property
    # def DELETE(self):
    #     self._DELETE = self.params
    #     return self._DELETE

    @property
    def params(self):

        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(dict(self.POST))
        return self._GETPOST


    @property
    def COOKIES(self):

        if self._COOKIES is None:
            raw_dict = Cookie.SimpleCookie(self._environ.get('HTTP_COOKIE', ''))
            self._COOKIES = {}
            for cookie in raw_dict.values():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES


class Response(threading.local):
    def bind(self):
        """ 清除老数据并创建一个新的Response对象 """
        self._COOKIES = None

        self.status = 200
        self.header = HeaderDict()
        self.content_type = 'text/html'
        self.error = None

    @property
    def COOKIES(self):
        if not self._COOKIES:
            self._COOKIES = Cookie.SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, **kargs):

        self.COOKIES[key] = value
        for k in kargs:
            self.COOKIES[key][k] = kargs[k]

    def get_content_type(self):

        return self.header['Content-Type']

    def set_content_type(self, value):
        self.header['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None, get_content_type.__doc__)


class HeaderDict(dict):
    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.title(), value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.title())

    def __delitem__(self, key):
        return dict.__delitem__(self, key.title())

    def __contains__(self, key):
        return dict.__contains__(self, key.title())

    def items(self):

        for key, values in dict.items(self):
            if not isinstance(values, list):
                values = [values]
            for value in values:
                yield (key, str(value))

    def add(self, key, value):

        if isinstance(value, list):
            for v in value:
                self.add(key, v)
        elif key in self:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
        else:
            self[key] = [value]




# 错误处理
######################################################################################################
def set_error_handler(code, handler):
    code = int(code)
    ERROR_HANDLER[code] = handler


def error(code=500):
    def wrapper(handler):
        set_error_handler(code, handler)
        return handler
    return wrapper


def run(server=WSGIRefServer, host='127.0.0.1', port=8080, **kargs):
    silent = bool('silent' in kargs and kargs['silent'])

    global DEBUG
    DEBUG = bool('DEBUG' in kargs and kargs['DEBUG'])

    if isinstance(server, type) and issubclass(server, BaseServer):
        server = server(host=host, port=port, **kargs)
    else:
        raise RuntimeError("Server must be a subclass of BaseServer")

    if not silent:
        print('Globefish server starting up (using %s)...' % repr(server))
        print('Listening on http://%s:%d/' % (server.host, server.port))
        print('Use Ctrl-C to quit.')

    try:
        server.run(WSGIHandler)
    except KeyboardInterrupt:
        print("The End...")


# 初始化
route = Router.route
request = Request()
response = Response()
DEBUG = False

ERROR_HANDLER = {}
HTTP_CODES = {
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}


@error(500)
def error500(exception):
    global DEBUG
    if DEBUG:
        error_html = """
        ERROR INFORMATION:<br>
         """
        error_html += "<br>\n".join(traceback.format_exc(10).splitlines()).replace('  ', '&nbsp;&nbsp;')
        error_html += """ <br><br>You're seeing this error because you have DEBUG = True when you run your server.
        Change that to False, and you will get a standard 500 page.<br><br>"""
    else:
        error_html = "<b>Error:</b> Internal server error."
    return error_html


def error_default(exception):
    status = response.status
    title = HTTP_CODES.get(status, 'Unknown').title()
    url = request.path
    error_html = """
    <!DOCTYPE >
    <html><head><title>Error %d: %s</title></head>
    <body><h1>Error %d: %s</h1>
    <p>Sorry, the requested URL %s caused an error.</p>

    """ % (status, title, status, title, url)
    if hasattr(exception, 'output'):
        error_html += exception.output
    error_html += """</body></html>"""
    return error_html
