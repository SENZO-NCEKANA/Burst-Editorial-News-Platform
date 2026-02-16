"""
News application models for managing users, articles, and publications.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model with role-based fields for readers and journalists.
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
        ('publisher', 'Publisher'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader',
        validators=[MinLengthValidator(3)]
    )

    # Fields for readers
    publisher_subscriptions = models.ManyToManyField(
        'Publisher',
        related_name='subscribers',
        blank=True
    )
    journalist_subscriptions = models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False,
        blank=True,
        limit_choices_to={'role': 'journalist'}
    )

    # Fields for journalists
    independent_articles = models.ManyToManyField(
        'Article',
        related_name='independent_author',
        blank=True
    )
    independent_newsletters = models.ManyToManyField(
        'Newsletter',
        related_name='independent_author',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_reader(self):
        """Check if user is a reader."""
        return self.role == 'reader'

    def is_editor(self):
        """Check if user is an editor."""
        return self.role == 'editor'

    def is_journalist(self):
        """Check if user is a journalist."""
        return self.role == 'journalist'

    def is_publisher(self):
        """Check if user is a publisher."""
        return self.role == 'publisher'


class Publisher(models.Model):
    """
    Model representing a publication/publisher.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    owner = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_publishers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    editors = models.ManyToManyField(
        User,
        related_name='publisher_editors',
        limit_choices_to={'role': 'editor'}
    )
    journalists = models.ManyToManyField(
        User,
        related_name='publisher_journalists',
        limit_choices_to={'role': 'journalist'}
    )

    class Meta:
        """
        Meta options for Publisher model.
        """
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Model for article categories.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        """
        Meta options for Category model.
        """
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Model representing a news article.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    hero_image = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_articles',
        limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_articles',
        limit_choices_to={'role': 'editor'}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        Meta class for Article model.
        """
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def hero_image_url(self):
        """Safely return hero image URL, or None if no file."""
        try:
            if self.hero_image:
                return self.hero_image.url
        except (ValueError, AttributeError):
            pass
        return None

    @property
    def reading_time_minutes(self):
        """Estimate reading time in minutes (~200 words per minute)."""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def approve(self, editor):
        """Approve article by editor."""
        self.is_approved = True
        self.status = 'approved'
        self.approved_by = editor
        self.approved_at = timezone.now()
        self.save()


class Newsletter(models.Model):
    """
    Model representing a newsletter.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    cover_image = models.ImageField(
        upload_to='newsletters/%Y/%m/',
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_newsletters',
        limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for Newsletter model.
        """
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def cover_image_url(self):
        """Safely return cover image URL, or None if no file."""
        try:
            if self.cover_image:
                return self.cover_image.url
        except (ValueError, AttributeError):
            pass
        return None


class Subscription(models.Model):
    """
    Model for managing user subscriptions.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscriptions'
    )
    journalist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscribed_to_journalist',
        limit_choices_to={'role': 'journalist'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta class for Subscription model.
        """
        unique_together = [
            ('user', 'publisher'),
            ('user', 'journalist')
        ]

    def __str__(self):
        if self.publisher:
            return f"{self.user} subscribes to {self.publisher}"
        return f"{self.user} subscribes to {self.journalist}"


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        """
        Meta class for PasswordResetToken model.
        """
        ordering = ['-created_at']

    def __str__(self):
        return f"Password reset token for {self.user.username}"

    def is_valid(self):
        """
        Check if token is valid (not used and not expired).
        """
        from datetime import timedelta

        if self.is_used:
            return False

        # Token expires after 24 hours
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() < expiry_time

    def is_expired(self):
        """
        Check if token is expired.
        """
        return not self.is_valid()
