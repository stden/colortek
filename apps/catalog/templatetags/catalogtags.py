# -*- coding: UTF-8 -*-

from django import template
from django.template.loader import render_to_string

from apps.catalog.models import Vote, VoteAtom, VoteKlass, VoteItem,\
    ServiceTerm
from apps.catalog.forms import generate_vote_form, VoteOrderForm
from apps.core.helpers import get_object_or_None
from django.contrib.auth.models import User
from django.template import Library, Node, TemplateSyntaxError

register = template.Library()


@register.simple_tag
def gather_rating(service, template='catalog/include/gather_rating.html'):
    container = service.containers.latest('id')
    # it's better reload mean atoms somewhere out of every
    # time tag's run, please use cron or celery
    # container.reload_atom_ratings()
    atoms = container.get_atom_ratings()

    return render_to_string(template, {
        'atoms': atoms
    })

@register.simple_tag
def get_term(service, code, default):
    if isinstance(service, User):
        term = get_object_or_None(
            ServiceTerm, service=service.service, code=code
        )
    else:
        term = get_object_or_None(ServiceTerm, service=service, code=code)
    return getattr(term, 'term') if hasattr(term, 'term') else default


class GenerateVoteFormNode(Node):
    def __init__(self, vote, varname):
        self.vote = vote
        self.varname = varname

    def render(self, context):
        vote = self.vote.resolve(context, ignore_failures=True)
        if isinstance(vote, Vote):
            form_class = generate_vote_form(vote, VoteOrderForm)
            context[self.varname] = form_class(None, instance=vote)
        return ''


@register.tag(name='generate_vote_form')
def generate_vote_form_tag(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(
               "generate_vote_form vote as form")
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    vote = parser.compile_filter(bits[1])
    varname = bits[3]
    return GenerateVoteFormNode(vote, varname)

