"""
my_filter
"""
from django import template
register = template.Library()
@register.filter(name='my_filter')
def my_filter(value):
    """
    my_filter
    :param value:
    :return:
    """
    delta = str(value).split("_")
    return delta
