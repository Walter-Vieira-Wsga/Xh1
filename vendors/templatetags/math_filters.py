# vendors/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica dois valores"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0