# -*- coding: utf-8 -*-

# 模板模块
#####################################################################################

# 基础模板类
from globefish.core import GlobefishException
from jinja2 import Environment, FileSystemLoader
from jinja2 import Template as jinja2_Template

try:
    from setting import TEMPLATE_DIRS
except ImportError:
    TEMPLATE_DIRS = 'templates'


class TemplateError(GlobefishException):
    pass


class BaseTemplate(object):
    def __init__(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


# 模板类，基于jinja2
class Template(BaseTemplate):
    def __init__(self, template=None):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIRS))
        if template:
            self.tmpl = jinja2_Template(template)

    def load(self, template_name):
        try:
            self.tmpl = self.env.get_template(template_name)
        except BaseException as e:
            raise TemplateError("error in " + e.message)

    def render(self, *args, **kwargs):
        return str(self.tmpl.render(*args, **kwargs))


# 模板的快捷使用方式
def render_template(template_name, *args, **kwargs):
    try:
        tmpl = Template()
        tmpl.load(template_name)
        return tmpl.render(*args, **kwargs)
    except BaseException as e:
        raise TemplateError("error in " + e.message)