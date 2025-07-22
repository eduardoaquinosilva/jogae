from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """Multiplies the arg and the value."""
    try:
        return value * arg
    except (ValueError, TypeError):
        # Return an empty string or 0 if multiplication fails
        return ''