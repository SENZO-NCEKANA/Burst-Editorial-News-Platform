"""
API URL configuration for news application.
"""

from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Articles
    path('articles/', api_views.ArticleListAPIView.as_view(),
         name='article-list'),
    path('articles/<int:pk>/', api_views.ArticleDetailAPIView.as_view(),
         name='article-detail'),
    path('articles/<int:pk>/approve/', api_views.approve_article_api,
         name='article-approve'),

    # Publishers
    path('publishers/', api_views.PublisherListAPIView.as_view(),
         name='publisher-list'),
    path('publishers/<int:pk>/', api_views.PublisherDetailAPIView.as_view(),
         name='publisher-detail'),

    # Categories
    path('categories/', api_views.CategoryListAPIView.as_view(),
         name='category-list'),

    # Newsletters
    path('newsletters/', api_views.NewsletterListAPIView.as_view(),
         name='newsletter-list'),

    # Subscriptions
    path('subscriptions/', api_views.SubscriptionListAPIView.as_view(),
         name='subscription-list'),
    path('subscriptions/<int:pk>/',
         api_views.SubscriptionDetailAPIView.as_view(),
         name='subscription-detail'),
    path('user-subscriptions/', api_views.user_subscriptions_api,
         name='user-subscriptions'),
]
