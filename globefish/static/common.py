# -*- coding: utf-8 -*-

# 静态文件模块
#####################################################################################
import mimetypes
import os
import time

from globefish.core import HTTPError, response, BreakTheGlobefish


def static_file(filename, root, mimetype='auto'):
    """ 返回一个静态文件作为Response响应. """
    root = os.path.abspath(root) + '/'
    filename = os.path.normpath(filename).strip('/')
    filename = os.path.join(root, filename)
    headers = dict()

    if not filename.startswith(root):
        raise HTTPError(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        raise HTTPError(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        raise HTTPError(401, "You do not have permission to access this file.")

    if mimetype == 'auto':
        guess = mimetypes.guess_type(filename)[0]
        if guess:
            response.content_type = guess
        elif mimetype:
            response.content_type = mimetype
    elif mimetype:
        response.content_type = mimetype

    stats = os.stat(filename)
    if 'Content-Length' not in response.header:
        response.header['Content-Length'] = stats.st_size
    if 'Last-Modified' not in response.header:
        ts = time.gmtime(stats.st_mtime)
        ts = time.strftime("%a, %d %b %Y %H:%M:%S +0000", ts)
        response.header['Last-Modified'] = ts

    raise BreakTheGlobefish(open(filename, 'r'))