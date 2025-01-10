from django import template

register = template.Library()


# Фильтр для получения значения атрибута
@register.filter(name='attr')
def attr(obj, field_name):
    return getattr(obj, field_name, '')


# Фильтр для проверки наличия атрибута
@register.filter(name='has_attr')
def has_attr(obj, attr_name):
    return hasattr(obj, attr_name)


# Фильтр для вызова метода или получения атрибута с проверкой
@register.filter(name='get_attr')
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)


# Фильтр для получения результата выполнения метода
@register.filter
def call_with_arg(method, arg):
    if callable(method):
        return method(arg)
    return method


# Фильтр подтверждения, что аргумент является методом
@register.filter(name='callable')
def callable(value):
    return hasattr(value, '__call__')


@register.filter(name='add_id')
def add_id(value):
    return f"{value}_id"


