"""
RSS feed for published articles.
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags

from .models import Article


class BurstArticleFeed(Feed):
    """RSS feed of latest published articles."""
    title = 'Burst - Latest News'
    link = '/'
    description = 'Latest published articles from Burst.'
    feed_type = Rss201rev2Feed

    def items(self):
        return Article.objects.filter(
            status='published'
        ).select_related('author', 'publisher', 'category').order_by('-created_at')[:50]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.summary:
            return item.summary
        text = strip_tags(item.content)
        return text[:500] + '...' if len(text) > 500 else text

    def item_link(self, item):
        return reverse('news:article_detail', args=[item.pk])

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_pubdate(self, item):
        return item.created_at
