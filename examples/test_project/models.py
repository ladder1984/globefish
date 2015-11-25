#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
database_proxy = Proxy()

class Person(Model):
    name = CharField()
    age = IntegerField()

    def say_hi(self):
        print("hi,I am ", self.name)

    class Meta:
        database = database_proxy


class Pet(Model):
    name = CharField()

    def say_hi(self):
        print("hi,I am ", self.name)

    class Meta:
        database = database_proxy



models_list = [Person,Pet]