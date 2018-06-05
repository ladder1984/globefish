# -*- coding: utf-8 -*-
from globefish.server.common import BaseServer


class CherryPyServer(BaseServer):
    def run(self, handler):
        from cherrypy import wsgiserver

        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.start()