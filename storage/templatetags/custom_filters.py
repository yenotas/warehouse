from django import template

register = template.Library()


@register.filter(name='ends_with')
def ends_with(value, suffix):
    """Проверяет, оканчивается ли строка на указанный суффикс."""
    return value.endswith(suffix)


@register.filter(name='replace_suffix')
def replace_suffix(value, old_suffix, new_suffix):
    """Заменяет суффикс в строке."""
    if value.endswith(old_suffix):
        return value[:-len(old_suffix)] + new_suffix
    return value


@register.filter(name='test_filter')
def test_filter(value):
    return "Фильтр работает!"


@register.filter(name='add_id')
def add_id(value):
    return f"{value}_id"
