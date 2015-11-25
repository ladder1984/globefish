#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 静态文件配置
STATIC_URL = './static'
#模板目录配置
TEMPLATE_DIRS = 'templates'

#数据库配置
database_type = 'SqliteDatabase'
database = 'guestbook.db'