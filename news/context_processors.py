"""
Context processors for global template variables.
"""
from django.conf import settings

from .models import Category, Publisher


def site_settings(request):
    """Add SITE_URL, site name, categories, and publishers to template context."""
    return {
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'SITE_NAME': 'Burst',
        'categories': Category.objects.all().order_by('name'),
        'publishers': Publisher.objects.all().order_by('name'),
    }
