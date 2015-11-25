#!/usr/bin/env python
# -*- coding: utf-8 -*-
from globefish.core import *
# from peewee import *
# from jinja2 import *
import datetime
from models import *
from globefish.utilities import init_db, redirect, abort
from globefish.utilities import server_static


sys.path.append(".")

connection = init_db()

one_person = Person()

# one_person.id = 4
one_person.name = u"aaaa"
one_person.age = 19
# one_person.name = "abcde"
one_person.save()

my_pet = Pet()
my_pet.name = "globefish"


@route('/')
def index():
    name = my_pet.name


    return "Hello,", str(name), "!"


# 快捷加载模板
@route('/now')
def now_time():
    now = datetime.datetime.now()
    # print(now)
    return render_template('now.html', now=now)


# 字符串模板
@route('/t')
def t():
    name = 'abcde'
    tmpl = Template('Hello {{ name }}!')
    return tmpl.render(name=name)


# 手动加载模板
@route('/t2')
def t2():
    name = 't22222'
    try:
        tmpl = Template()
        tmpl.load('now.html')
        return tmpl.render(now=name)
    except BaseException as e:
        print(e)
        return "000"


@route('/500page')
def raise_an_500error():
    return 1 / 0


# 静态文件
@route('/static/test.file')
def test_static(filename):
    static_file(filename, root='./static')


# url参数
@route('/hello/:name')
def hello_name(name):
    return 'Hello %s!' % name


@route('/post-test', method='POST')
def hello_post():
    name = request.POST['name']
    print("data from post:", name)
    return 'Hello %s!' % name


@route('/put-test', method='PUT')
def put_test():
    try:

        print("data in request.PUT:", request.PUT['name'])
        return "OK"
        print("OK")
    except BaseException as e:
        print(e)

    return 'false'


@route('/get-test', method='GET')
def get_test():
    try:
        print(request.GET['name'])
    except BaseException as e:
        print(e)
    return 'get'



@route('/a-b')
def a_b():
    return "a-b"


@route('/counter')
def counter():
    old = request.COOKIES.get('counter', 0)
    new = int(old) + 1
    response.COOKIES['counter'] = new
    return "You viewed this page %d times!" % new


def test_add():
    return "success"


@route('/wrong/url')
def wrong():
    redirect("/right/url")

@route('/right/url')
def right():
    return "right url"





@route('/restricted')
def restricted():
    abort(401, "Sorry, access denied.")


@route('/error-test')
def error_test():
    raise BreakTheglobefish('这是一个手动错误')

# add_route('/test-add',test_add)

run(host='localhost', port=6600, DEBUG=True)



