from django import template

register = template.Library()

@register.filter
def is_selected(value, arg):
    """
    Returns True if value matches arg as a string.
    Usage: value|is_selected:"1"
    """
    if value is None:
        return False
    return str(value) == str(arg)
