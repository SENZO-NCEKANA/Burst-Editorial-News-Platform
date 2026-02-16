"""
Custom adapters for django-allauth to work with news.User model.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Ensures new social sign-up users get role='reader' and defaults."""

    def populate_user(self, request, sociallogin, data):
        """Set default role for social sign-ups."""
        user = super().populate_user(request, sociallogin, data)
        role = getattr(user, 'role', None)
        if hasattr(User, 'role') and not role:
            user.role = 'reader'
        return user
