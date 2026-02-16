"""
Management command to set up user groups and permissions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Newsletter, Publisher, Category


class Command(BaseCommand):
    """
    Command to create user groups with appropriate permissions.
    """
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        """
        Create groups and assign permissions.
        """
        # Get content types
        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(Newsletter)
        publisher_ct = ContentType.objects.get_for_model(Publisher)
        category_ct = ContentType.objects.get_for_model(Category)

        # Create Reader group
        reader_group, created = Group.objects.get_or_create(name='Reader')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created Reader group')
            )

        # Reader permissions (view only)
        reader_permissions = [
            Permission.objects.get(
                codename='view_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='view_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='view_publisher',
                content_type=publisher_ct
            ),
            Permission.objects.get(
                codename='view_category',
                content_type=category_ct
            ),
        ]

        reader_group.permissions.set(reader_permissions)
        self.stdout.write(
            self.style.SUCCESS('Assigned permissions to Reader group')
        )

        # Create Journalist group
        journalist_group, created = Group.objects.get_or_create(
            name='Journalist')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created Journalist group')
            )

        # Journalist permissions (create, view, update, delete articles and
        # newsletters)
        journalist_permissions = [
            Permission.objects.get(
                codename='add_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='view_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='change_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='delete_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='add_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='view_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='change_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='delete_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='view_publisher',
                content_type=publisher_ct
            ),
            Permission.objects.get(
                codename='view_category',
                content_type=category_ct
            ),
        ]

        journalist_group.permissions.set(journalist_permissions)
        self.stdout.write(
            self.style.SUCCESS('Assigned permissions to Journalist group')
        )

        # Create Editor group
        editor_group, created = Group.objects.get_or_create(name='Editor')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created Editor group')
            )

        # Editor permissions (view, update, delete articles and newsletters)
        editor_permissions = [
            Permission.objects.get(
                codename='view_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='change_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='delete_article',
                content_type=article_ct
            ),
            Permission.objects.get(
                codename='view_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='change_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='delete_newsletter',
                content_type=newsletter_ct
            ),
            Permission.objects.get(
                codename='view_publisher',
                content_type=publisher_ct
            ),
            Permission.objects.get(
                codename='change_publisher',
                content_type=publisher_ct
            ),
            Permission.objects.get(
                codename='view_category',
                content_type=category_ct
            ),
            Permission.objects.get(
                codename='change_category',
                content_type=category_ct
            ),
        ]

        editor_group.permissions.set(editor_permissions)
        self.stdout.write(
            self.style.SUCCESS('Assigned permissions to Editor group')
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully set up all groups and permissions'
            )
        )
