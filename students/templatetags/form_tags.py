from django import template
register = template.Library()

@register.filter
def add_class(value, css_class):
    """
    Add a CSS class to a form field or handle string values
    """
    if hasattr(value, 'as_widget'):
        # It's a form field
        return value.as_widget(attrs={"class": css_class})
    else:
        # It's already a string, so we can't modify it this way
        return value