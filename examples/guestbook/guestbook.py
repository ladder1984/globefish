# -*- coding: utf-8 -*-
import datetime

from globefish.core import *
from globefish.template.common import render_template
from models import *
from globefish.utilities import init_db


connection = init_db()


@route('/')
def index():
    title = "留言板"
    message_list = Message.select().order_by(-Message.created_at)
    return render_template('index.html', message_list=message_list, title=title)


@route("add", method='POST')
def add_message():
    try:
        message = Message()
        message.username = request.POST['username']
        message.email = request.POST['email']
        message.content = request.POST['content']
        message.created_at = datetime.datetime.now()
        message.save()
        return "OK"
    except BaseException as e:
        print(e)


run(host='localhost', port=6700, DEBUG=True)
