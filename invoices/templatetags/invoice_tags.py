# invoices/templatetags/invoice_tags.py
from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def mult(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0