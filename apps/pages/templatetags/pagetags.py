from django import template
from apps.pages.models import TextBlock

register = template.Library()

@register.inclusion_tag('pages/templatetags/textblock.html')
def textblock(codename):
    try:
        return {'textblock': TextBlock.objects.get(codename=codename)}
    except TextBlock.DoesNotExist:
        return {'textblock': ''}
