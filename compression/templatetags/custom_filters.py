from django import template
from django.template.defaultfilters import filesizeformat

register = template.Library()

@register.filter
def custom_filesizeformat(bytes_value):
    """Custom file size formatting"""
    return filesizeformat(bytes_value)
