from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def clp(value):
    try:
        value = int(value)
        return "$" + intcomma(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
