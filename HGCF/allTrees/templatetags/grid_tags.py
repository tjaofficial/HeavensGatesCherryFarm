from django import template # type: ignore

register = template.Library()

@register.filter
def get_key_from_string(item, key):
    return item[key]