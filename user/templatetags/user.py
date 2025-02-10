from django import template

register = template.Library()


@register.filter
def get_attribute(obj, field_name):
    return getattr(obj, field_name)
