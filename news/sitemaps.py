"""
Sitemap for SEO.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article


class StaticViewSitemap(Sitemap):
    """Static pages for sitemap."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ['news:home', 'news:article_list', 'news:search_articles',
                'news:terms', 'news:privacy', 'news:login', 'news:register']

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    """Published articles for sitemap."""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Article.objects.filter(status='published').order_by('-created_at')

    def location(self, item):
        return reverse('news:article_detail', args=[item.pk])

    def lastmod(self, obj):
        return obj.updated_at
