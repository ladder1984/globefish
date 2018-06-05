# -*- coding: utf-8 -*-
from globefish.server.common import BaseServer


class WSGIRefServer(BaseServer):
    def run(self, handler):
        from wsgiref.simple_server import make_server

        server = make_server(self.host, self.port, handler)
        server.serve_forever()