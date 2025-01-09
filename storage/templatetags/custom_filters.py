from django import template

register = template.Library()


@register.filter(name='attr')
def attr(obj, field_name):
    return getattr(obj, field_name, '')


@register.filter(name='test_filter')
def test_filter(value):
    return "Фильтр работает!"


@register.filter(name='add_id')
def add_id(value):
    return f"{value}_id"
