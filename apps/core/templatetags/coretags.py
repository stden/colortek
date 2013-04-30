# coding: utf-8
import re
import datetime
from datetime import timedelta
from django import template
from django.template import Library, Node, TemplateSyntaxError
from django.template.defaultfilters import striptags
from apps.core.helpers import get_object_or_None
from django.db.models import Q, get_model

register = Library()
class JSUrlNode(Node):
    def __init__(self, url):
        self.url = url
    def render(self, context):
        from django.core.urlresolvers import get_urlconf, get_resolver
        resolver = get_resolver(get_urlconf())
        jsurl = '/'
        if self.url in resolver.reverse_dict:
            url = resolver.reverse_dict[self.url][0][0][0]
            jsurl = re.sub(re.compile('\%(\(\w+\))\w'), '%s', url)
        return "/%(url)s" %  { 'url': jsurl }

@register.tag
def jsurl(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError, "jsurl takes one argument"
    url = bits[1]
    if url[1] in ('"', '"') and url[-1] in ('"', "'"):
        url = url[1:-1]
    return JSUrlNode(url)

class GetFormNode(Node):
    def __init__(self, init, varname, use_request):
        self.init = init[1:-1]
        self.varname = varname
        self.use_request = use_request

    def render(self, context):
        app = self.init[:self.init.rindex('.')]
        _form = self.init[self.init.rindex('.')+1:]
        module = __import__(app, 0, 0, -1)
        form_class = getattr(module, _form)
        context[self.varname] = form_class(request=context['request']) \
            if self.use_request else form_class()
        return ''

@register.tag
def get_form(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 4 and len(bits) != 5: #get_form 'apps.' for varname [use request]
        raise (TemplateSyntaxError,
               "get_form  'app.model.Form' for form [use_request]")
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    init = bits[1]
    varname = bits[3]
    use_request = bool(bits[4]) if len(bits) > 4 else False
    return GetFormNode(init, varname, use_request)


class GetInstancesNode(Node):
    def __init__(self, app_n_model, varname, slice=False):
        self.app_n_model = app_n_model
        self.varname = varname
        self.slice = slice

    def render(self, context):
        ModelObject = get_model(*self.app_n_model.split('.'))
        safe_all = reduce(
            lambda x, y: getattr(x, y) if hasattr(x, y) else None,
            [ModelObject, 'objects', 'all']
        )
        if self.slice:
            count = safe_all().count()
            objects = []
            objects_n1 = safe_all()[count/2:]
            objects_n2 = safe_all()[:count/2]
            objects.append(objects_n1)
            objects.append(objects_n2)
            context[self.varname] = objects
            return ''

        context[self.varname] = safe_all
        return ''

@register.tag
def get_instances(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) < 4 or len(bits) > 5:
        raise TemplateSyntaxError(
               "get_instances  'application.model' as varname ['slice']")
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    app_n_model = bits[1][1:-1]
    varname = bits[3]
    slice = False
    if len(bits) == 5:
        slice = bool(bits[4][1:-1]) if bits[4] else False
    return GetInstancesNode(app_n_model, varname, slice)

class SliceInstancesNode(Node):
    def __init__(self, qset, varname):
        self.qset = qset
        self.varname = varname

    def render(self, context):
        qset = self.qset.resolve(context, ignore_failures=True)
        if hasattr(qset, 'count') and not isinstance(qset, basestring):
            count = qset.count()
            objects = []
            objects_n1 = qset[count/2:]
            objects_n2 = qset[:count/2]
            objects.append(objects_n1)
            objects.append(objects_n2)
            context[self.varname] = objects
        return ''

@register.tag
def slice_instances(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(
               "slice_instances qset as varname")
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    qs = parser.compile_filter(bits[1])
    varname = bits[3]
    return SliceInstancesNode(qs, varname)

def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)
raw = register.tag(raw)
