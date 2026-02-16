"""
Forms for news application with validation and user-friendly interfaces.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Article, Publisher, Category, Newsletter, Subscription
)


class UserRegistrationForm(UserCreationForm):
    """
    Custom user registration form with role selection.
    Supports publisher selection for editors/journalists and
    publisher creation for publisher role.
    """
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # For editor/journalist: select existing publisher
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        empty_label='-- Select a publisher --',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # For publisher role: create new publishing house
    publisher_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of your publishing house'
        })
    )
    publisher_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description (optional)'
        })
    )
    publisher_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com (optional)'
        })
    )

    class Meta:
        """
        Meta options for UserRegistrationForm.
        """
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'role', 'password1', 'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['publisher'].queryset = Publisher.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        publisher = cleaned_data.get('publisher')
        publisher_name = cleaned_data.get('publisher_name', '').strip()

        if role == 'editor':
            if not publisher:
                self.add_error(
                    'publisher',
                    'Editors must be assigned to a publisher.'
                )
        elif role == 'publisher':
            if not publisher_name:
                self.add_error(
                    'publisher_name',
                    'Please enter your publishing house name.'
                )
            else:
                if Publisher.objects.filter(name__iexact=publisher_name).exists():
                    self.add_error(
                        'publisher_name',
                        'A publisher with this name already exists.'
                    )
        return cleaned_data


class PublisherForm(forms.ModelForm):
    """
    Form for creating and editing publishers (staff only).
    """
    class Meta:
        model = Publisher
        fields = ['name', 'description', 'website', 'owner']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief description'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'owner': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(role='publisher')
        self.fields['owner'].required = False
        self.fields['website'].required = False


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles.
    """
    class Meta:
        """
        Meta options for ArticleForm.
        """
        model = Article
        fields = [
            'title', 'content', 'summary', 'hero_image',
            'publisher', 'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter article content'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter article summary (optional)'
            }),
            'hero_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].queryset = Publisher.objects.all()
        self.fields['category'].queryset = Category.objects.all()

    def clean_hero_image(self):
        """Validate hero image type and size."""
        image = self.cleaned_data.get('hero_image')
        if not image:
            return image

        allowed_types = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
        if hasattr(image, 'content_type') and image.content_type not in allowed_types:
            raise forms.ValidationError(
                'Invalid image type. Use JPEG, PNG, GIF, or WebP.'
            )

        max_size = 5 * 1024 * 1024  # 5 MB
        if image.size > max_size:
            raise forms.ValidationError(
                'Image too large. Maximum size is 5 MB.'
            )

        return image


class ArticleApprovalForm(forms.ModelForm):
    """
    Form for editors to approve articles.
    """
    class Meta:
        """
        Meta options for ArticleApprovalForm.
        """
        model = Article
        fields = ['status', 'is_approved']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
        }


class NewsletterForm(forms.ModelForm):
    """
    Form for creating newsletters.
    """
    class Meta:
        """
        Meta options for NewsletterForm.
        """
        model = Newsletter
        fields = ['title', 'content', 'cover_image', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter newsletter title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter newsletter content'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].queryset = Publisher.objects.all()

    def clean_cover_image(self):
        """Validate cover image type and size."""
        image = self.cleaned_data.get('cover_image')
        if not image:
            return image

        allowed_types = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
        if hasattr(image, 'content_type') and image.content_type not in allowed_types:
            raise forms.ValidationError(
                'Invalid image type. Use JPEG, PNG, GIF, or WebP.'
            )

        max_size = 5 * 1024 * 1024  # 5 MB
        if image.size > max_size:
            raise forms.ValidationError(
                'Image too large. Maximum size is 5 MB.'
            )

        return image


class SubscriptionForm(forms.ModelForm):
    """
    Form for managing subscriptions.
    """
    class Meta:
        """
        Meta options for SubscriptionForm.
        """
        model = Subscription
        fields = ['publisher', 'journalist']
        widgets = {
            'publisher': forms.Select(attrs={'class': 'form-control'}),
            'journalist': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].queryset = Publisher.objects.all()
        self.fields['journalist'].queryset = User.objects.filter(
            role='journalist'
        )
        self.fields['publisher'].required = False
        self.fields['journalist'].required = False

    def clean(self):
        cleaned_data = super().clean()
        publisher = cleaned_data.get('publisher')
        journalist = cleaned_data.get('journalist')

        if not publisher and not journalist:
            raise forms.ValidationError(
                'You must subscribe to either a publisher or a journalist.'
            )

        return cleaned_data


class SearchForm(forms.Form):
    """
    Form for searching articles.
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        empty_label="All Publishers",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ForgotPasswordForm(forms.Form):
    """
    Form for requesting password reset.
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )


class AddTeamMemberForm(forms.Form):
    """
    Form for publishers to add editors or journalists to their publishing house.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    role = forms.ChoiceField(
        choices=[('editor', 'Editor'), ('journalist', 'Journalist')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ResetPasswordForm(forms.Form):
    """
    Form for resetting password with token.
    """
    new_password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return cleaned_data
