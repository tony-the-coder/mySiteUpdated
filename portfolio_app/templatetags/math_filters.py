# LehmanCustomConstruction/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter(name='mult')
def mult(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try: # Try float if int conversion fails
            return float(value) * float(arg)
        except (ValueError, TypeError):
            return '' # Or handle error as you see fit