import hashlib

from django import template

register = template.Library()


@register.filter
def get_form_field(form, field_name):
    return form[field_name]


@register.filter
def md5(value):
    return hashlib.md5(str(value).encode()).hexdigest()
