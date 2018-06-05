# -*- coding: utf-8 -*-


# 路由模块
#####################################################################################
import re

ROUTES_SIMPLE = {}
ROUTES_REGEXP = {}


class Router(object):
    @classmethod
    def add_route(cls, url, handler, method='GET'):
        method = method.strip().upper()
        url = url.strip().lstrip('$^/ ').rstrip('$^ ')
        if re.match(r'^(\w+/)*\w*$', url):
            ROUTES_SIMPLE.setdefault(method, {})[url] = handler
        else:
            url = cls.compile_route(url)
            ROUTES_REGEXP.setdefault(method, []).append([url, handler])

    @classmethod
    def route(cls, url, **kargs):
        def wrapper(handler):
            cls.add_route(url, handler, **kargs)
            return handler

        return wrapper

    @classmethod
    def compile_route(cls, route):
        route = re.sub(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)', r'(?P<\1>\g<re>)', route)
        route = re.sub(r':([a-zA-Z_]+)', r'(?P<\1>[^/]+)', route)
        return re.compile('^%s$' % route)

    @classmethod
    def match_url(cls, url, method='GET'):

        url = url.strip().lstrip("/ ")
        route = ROUTES_SIMPLE.get(method, {}).get(url, None)
        if route:
            return (route, {})

        routes = ROUTES_REGEXP.get(method, [])
        for i in xrange(len(routes)):
            match = routes[i][0].match(url)
            if match:
                handler = routes[i][1]
                if i > 0:
                    routes[i - 1], routes[i] = routes[i], routes[i - 1]
                return (handler, match.groupdict())
        return (None, None)
