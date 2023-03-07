from django import template

register = template.Library()

@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)

@register.filter(name='range')
def ttrange(a, b):
  return range(a, b)