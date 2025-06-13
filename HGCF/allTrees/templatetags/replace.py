from django import template # type: ignore

register = template.Library()

@register.filter
def replace(string, find_replace):
    find, replace = find_replace.split(":")
    return string.replace(find, replace)