from django import template

register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    """Вычитает arg из value"""
    return value - arg