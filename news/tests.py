"""
Unit tests for news application models, views, and API.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import (
    Publisher, Category, Article, Subscription
)

User = get_user_model()


class UserModelTest(TestCase):
    """
    Test cases for User model.
    """
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='reader'
        )

    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'reader')
        self.assertTrue(self.user.is_reader())

    def test_user_roles(self):
        """Test user role methods."""
        self.assertTrue(self.user.is_reader())
        self.assertFalse(self.user.is_editor())
        self.assertFalse(self.user.is_journalist())

        # Test editor role
        editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )
        self.assertTrue(editor.is_editor())

        # Test journalist role
        journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )
        self.assertTrue(journalist.is_journalist())


class PublisherModelTest(TestCase):
    """
    Test cases for Publisher model.
    """
    def setUp(self):
        """Set up test data."""
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher',
            website='https://testpublisher.com'
        )

    def test_publisher_creation(self):
        """Test publisher creation."""
        self.assertEqual(self.publisher.name, 'Test Publisher')
        self.assertEqual(str(self.publisher), 'Test Publisher')


class ArticleModelTest(TestCase):
    """
    Test cases for Article model.
    """
    def setUp(self):
        """Set up test data."""
        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech news'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            summary='Test summary',
            author=self.journalist,
            publisher=self.publisher,
            category=self.category
        )

    def test_article_creation(self):
        """Test article creation."""
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.status, 'draft')
        self.assertFalse(self.article.is_approved)

    def test_article_approval(self):
        """Test article approval."""
        editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )

        self.article.approve(editor)
        self.assertTrue(self.article.is_approved)
        self.assertEqual(self.article.status, 'published')
        self.assertEqual(self.article.approved_by, editor)


class SubscriptionModelTest(TestCase):
    """
    Test cases for Subscription model.
    """
    def setUp(self):
        """Set up test data."""
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='testpass123',
            role='reader'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )
        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )

    def test_publisher_subscription(self):
        """Test publisher subscription."""
        subscription = Subscription.objects.create(
            user=self.reader,
            publisher=self.publisher
        )
        self.assertEqual(subscription.user, self.reader)
        self.assertEqual(subscription.publisher, self.publisher)
        self.assertIsNone(subscription.journalist)

    def test_journalist_subscription(self):
        """Test journalist subscription."""
        subscription = Subscription.objects.create(
            user=self.reader,
            journalist=self.journalist
        )
        self.assertEqual(subscription.user, self.reader)
        self.assertEqual(subscription.journalist, self.journalist)
        self.assertIsNone(subscription.publisher)


class ArticleViewTest(TestCase):
    """
    Test cases for article views.
    """
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='testpass123',
            role='reader'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            author=self.journalist,
            publisher=self.publisher,
            status='published',
            is_approved=True
        )

    def test_home_view(self):
        """Test home view."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')

    def test_article_detail_view(self):
        """Test article detail view."""
        self.client.force_login(self.reader)
        response = self.client.get(f'/articles/{self.article.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')

    def test_create_article_requires_login(self):
        """Test that creating article requires login."""
        response = self.client.get('/articles/create/')
        self.assertRedirects(response, '/login/?next=/articles/create/')

    def test_create_article_requires_journalist_role(self):
        """Test that creating article requires journalist role."""
        User.objects.create_user(
            username='reader2',
            email='reader2@example.com',
            password='testpass123',
            role='reader'
        )
        self.client.login(username='reader2', password='testpass123')
        response = self.client.get('/articles/create/')
        self.assertRedirects(response, '/articles/')


class APITest(APITestCase):
    """
    Test cases for REST API.
    """
    def setUp(self):
        """Set up test data."""
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='testpass123',
            role='reader'
        )
        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )
        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )

        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )
        self.publisher.editors.add(self.editor)

        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            author=self.journalist,
            publisher=self.publisher,
            status='published'
        )

        # Create tokens for API authentication
        self.reader_token = Token.objects.create(user=self.reader)
        self.journalist_token = Token.objects.create(user=self.journalist)
        self.editor_token = Token.objects.create(user=self.editor)

    def test_article_list_api_requires_authentication(self):
        """Test that article list API requires authentication."""
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_list_api_with_authentication(self):
        """Test article list API with authentication."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.reader_token.key)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_article_api(self):
        """Test creating article via API."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.journalist_token.key)
        data = {
            'title': 'API Test Article',
            'content': 'This is a test article created via API.',
            'author_id': self.journalist.id,
            'publisher_id': self.publisher.id
        }
        response = self.client.post('/api/articles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_approve_article_api_requires_editor(self):
        """Test that approving article requires editor role."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.journalist_token.key
        )
        response = self.client.post(
            f'/api/articles/{self.article.pk}/approve/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_article_api_with_editor(self):
        """Test approving article with editor role."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.editor_token.key
        )
        response = self.client.post(
            f'/api/articles/{self.article.pk}/approve/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reader_sees_only_subscribed_articles(self):
        """Test that readers receive articles based on their subscriptions."""
        # Reader subscribes to publisher
        Subscription.objects.create(
            user=self.reader,
            publisher=self.publisher
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.reader_token.key)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Reader should see the article from subscribed publisher
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Article')

        # Reader with no subscriptions sees no articles
        reader2 = User.objects.create_user(
            username='reader2',
            email='reader2@example.com',
            password='testpass123',
            role='reader'
        )
        token2 = Token.objects.create(user=reader2)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_subscriptions_api(self):
        """Test user subscriptions API."""
        # Create subscription
        Subscription.objects.create(
            user=self.reader,
            publisher=self.publisher
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.reader_token.key)
        response = self.client.get('/api/user-subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('publishers', response.data)
        self.assertIn('articles', response.data)

    def test_publisher_list_api(self):
        """Test publisher list API."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.reader_token.key)
        response = self.client.get('/api/publishers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Publisher')

    def test_category_list_api(self):
        """Test category list API."""
        Category.objects.create(
            name='Technology',
            description='Tech news'
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.reader_token.key)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Technology')


class EmailNotificationTest(TestCase):
    """
    Test cases for email notifications.
    """
    def setUp(self):
        """Set up test data."""
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='testpass123',
            role='reader'
        )
        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )

        # Create subscription
        Subscription.objects.create(
            user=self.reader,
            publisher=self.publisher
        )

        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            author=self.journalist,
            publisher=self.publisher
        )

    def test_email_notification_on_approval(self):
        """Test that email is sent when article is approved."""
        # Clear mail outbox
        mail.outbox = []

        # Approve article
        editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )
        self.article.approve(editor)

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'New Article: Test Article')
        self.assertIn(self.reader.email, mail.outbox[0].to)


class PasswordResetTest(TestCase):
    """
    Test password reset functionality.
    """
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='reader'
        )

    def test_forgot_password_view_get(self):
        """Test forgot password view GET request."""
        response = self.client.get('/forgot-password/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Forgot Password')

    def test_forgot_password_view_post_valid_email(self):
        """Test forgot password view with valid email."""
        with self.settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            response = self.client.post('/forgot-password/', {
                'email': 'test@example.com'
            })
            self.assertRedirects(response, '/login/')
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Password Reset Request', mail.outbox[0].subject)

    def test_forgot_password_view_post_invalid_email(self):
        """Test forgot password view with invalid email."""
        response = self.client.post('/forgot-password/', {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_view_valid_token(self):
        """Test reset password view with valid token."""
        from news.models import PasswordResetToken
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='test-token-123'
        )

        response = self.client.get(f'/reset-password/{token.token}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset Password')

    def test_reset_password_view_invalid_token(self):
        """Test reset password view with invalid token."""
        response = self.client.get('/reset-password/invalid-token/')
        self.assertRedirects(response, '/forgot-password/')

    def test_reset_password_post_valid(self):
        """Test reset password POST with valid data."""
        from news.models import PasswordResetToken
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='test-token-123'
        )

        response = self.client.post(f'/reset-password/{token.token}/', {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertRedirects(response, '/login/')

        # Check that password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

        # Check that token was marked as used
        token.refresh_from_db()
        self.assertTrue(token.is_used)
