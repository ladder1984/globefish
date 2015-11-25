#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
from globefish.core import *


# 初始化models.py里的模块
def init_db():
    try:
        from setting import database, database_type
        from models import database_proxy, models_list
    except ImportError as e:
        raise ImportError(str(e) + "，" + "models、setting配置错误")
    if database_type is 'SqliteDatabase' or database_type is None:
        db = SqliteDatabase(database)
    elif database_type is 'MySQLDatabase':
        db = MySQLDatabase(database)
    elif database_type is 'PostgresqlDatabase':
        db = PostgresqlDatabase(database)
    else:
        raise StandardError(u"不支持的数据库类型")
    database_proxy.initialize(db)
    db.connect()

    try:
        db.create_tables(models_list)
    except:
        pass

    return db


# 处理静态文件
@route('/static/:filename#.*#')
def server_static(filename):
    static_file(filename, root='./static')


def redirect(url, code=307):
    response.status = code
    response.header['Location'] = url
    raise BreakTheGlobefish("")


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    raise HTTPError(code, text)
