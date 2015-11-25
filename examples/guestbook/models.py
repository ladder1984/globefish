#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *

database_proxy = Proxy()


class Message(Model):
    username = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField()

    class Meta:
        database = database_proxy


models_list = [Message]