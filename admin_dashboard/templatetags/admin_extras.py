from django import template
from vendors.models import Vendor

register = template.Library()


@register.simple_tag
def get_vendor_count():
    try:
        return Vendor.objects.count()
    except Exception:
        return 0
