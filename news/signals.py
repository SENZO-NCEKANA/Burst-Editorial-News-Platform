"""
Django signals for handling article approval notifications and social media
posting.
"""

import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Article, Subscription, User


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Assign user to group based on role when created. Covers OAuth sign-ups.
    """
    if created and not instance.groups.exists():
        try:
            if instance.role == 'reader':
                instance.groups.add(Group.objects.get(name='Reader'))
            elif instance.role == 'editor':
                instance.groups.add(Group.objects.get(name='Editor'))
            elif instance.role == 'journalist':
                instance.groups.add(Group.objects.get(name='Journalist'))
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """
    Handle article approval by sending emails and posting to X (Twitter).
    """
    if instance.is_approved and instance.status == 'approved':
        send_approval_notifications(instance)
        post_to_twitter(instance)


def send_approval_notifications(article):
    """
    Send email notifications to subscribers when article is approved.
    """
    # Get all subscribers for the article's publisher and journalist
    publisher_subscribers = []
    journalist_subscribers = []

    if article.publisher:
        publisher_subscribers = Subscription.objects.filter(
            publisher=article.publisher
        ).values_list('user__email', flat=True)

    if article.author:
        journalist_subscribers = Subscription.objects.filter(
            journalist=article.author
        ).values_list('user__email', flat=True)

    # Combine and deduplicate subscriber emails
    all_subscribers = set(publisher_subscribers) | set(journalist_subscribers)

    if all_subscribers:
        subject = f'New Article: {article.title}'

        # Create email content
        context = {
            'article': article,
            'site_url': (settings.SITE_URL if hasattr(settings, 'SITE_URL')
                         else 'http://localhost:8000')
        }

        html_message = render_to_string(
            'news/email/article_notification.html', context)
        plain_message = render_to_string(
            'news/email/article_notification.txt', context)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(
                    settings, 'DEFAULT_FROM_EMAIL',
                    'Burst <noreply@burst.app>'
                ),
                recipient_list=list(all_subscribers),
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email notifications: {e}")


def post_to_twitter(article):
    """
    Post article to Twitter when approved.
    """
    # Check if Twitter is enabled
    if not getattr(settings, 'TWITTER_ENABLED', False):
        print("Twitter posting disabled")
        return

    # Twitter API v2 endpoint for posting tweets
    twitter_api_url = "https://api.twitter.com/2/tweets"
    bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', None)

    # Create tweet content
    tweet_text = f"New Article: {article.title}\n\n{article.summary[:200]}..."
    if len(article.summary) > 200:
        tweet_text += "..."

    # Add article URL if available
    if hasattr(settings, 'SITE_URL'):
        tweet_text += (f"\n\nRead more: {settings.SITE_URL}/articles/"
                       f"{article.pk}/")

    # Prepare headers
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
    }

    # Prepare payload
    payload = {
        'text': tweet_text
    }

    try:
        response = requests.post(
            twitter_api_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 201:
            print(f"Successfully posted article '{article.title}' to Twitter")
        else:
            print(
                f"Failed to post to Twitter: {response.status_code} - "
                f"{response.text}"
            )

    except requests.exceptions.RequestException as e:
        print(f"Error posting to Twitter: {e}")


@receiver(post_save, sender=Article)
def update_article_status(sender, instance, created, **kwargs):
    """
    Update article status when approved.
    """
    if instance.is_approved and instance.status != 'published':
        instance.status = 'published'
        instance.save(update_fields=['status'])
