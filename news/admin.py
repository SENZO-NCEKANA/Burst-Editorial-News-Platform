"""
Admin configuration for news application models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Publisher, Category, Article, Newsletter, Subscription,
    PasswordResetToken
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for User model with role-based fields.
    """
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {
            'fields': ('role',)
        }),
        ('Reader Subscriptions', {
            'fields': ('publisher_subscriptions', 'journalist_subscriptions'),
            'classes': ('collapse',)
        }),
        ('Journalist Content', {
            'fields': ('independent_articles', 'independent_newsletters'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = (
        'publisher_subscriptions',
        'journalist_subscriptions',
        'independent_articles',
        'independent_newsletters',
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin for Publisher model.
    """
    list_display = ('name', 'owner', 'website', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    raw_id_fields = ('owner',)
    filter_horizontal = ('editors', 'journalists')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category model.
    """
    list_display = ('name',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin for Article model with approval workflow.
    """
    list_display = (
        'title', 'author', 'publisher', 'status', 'is_approved',
        'created_at', 'approved_by'
    )
    list_filter = (
        'status', 'is_approved', 'category', 'publisher',
        'created_at', 'approved_at'
    )
    search_fields = ('title', 'content', 'summary', 'author__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'approved_at')

    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'content', 'summary', 'category')
        }),
        ('Author & Publisher', {
            'fields': ('author', 'publisher')
        }),
        ('Status & Approval', {
            'fields': (
                'status', 'is_approved', 'approved_by',
                'approved_at', 'published_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filter articles based on user role."""
        qs = super().get_queryset(request)
        if request.user.is_editor():
            return qs.filter(publisher__editors=request.user)
        elif request.user.is_journalist():
            return qs.filter(author=request.user)
        return qs


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin for Newsletter model.
    """
    list_display = ('title', 'author', 'publisher', 'created_at')
    list_filter = ('publisher', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Newsletter Information', {
            'fields': ('title', 'content', 'cover_image')
        }),
        ('Author & Publisher', {
            'fields': ('author', 'publisher')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Admin for Subscription model.
    """
    list_display = ('user', 'publisher', 'journalist', 'created_at')
    list_filter = ('created_at', 'publisher')
    search_fields = (
        'user__username', 'publisher__name', 'journalist__username'
    )
    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Filter subscriptions based on user role."""
        qs = super().get_queryset(request)
        if request.user.is_reader():
            return qs.filter(user=request.user)
        return qs


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetToken model.
    """
    list_display = ('user', 'token', 'created_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'is_valid')

    def is_valid(self, obj):
        """Display if token is valid."""
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'
