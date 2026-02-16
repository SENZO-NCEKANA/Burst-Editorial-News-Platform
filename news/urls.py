"""
URL configuration for news application.
"""

from django.urls import path, include
from . import views
from .feeds import BurstArticleFeed

app_name = 'news'

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password,
         name='reset_password'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # Articles
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/create/', views.create_article, name='create_article'),
    path('articles/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('articles/<int:pk>/approve/', views.approve_article,
         name='approve_article'),

    # Subscriptions
    path('subscriptions/', views.subscription_management,
         name='subscription_management'),
    path('subscriptions/<int:pk>/delete/', views.delete_subscription,
         name='delete_subscription'),

    # Newsletters
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.create_newsletter,
         name='create_newsletter'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='newsletter_detail'),

    # Publishers (staff only)
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/create/', views.publisher_create, name='publisher_create'),
    path('publishers/<int:pk>/edit/', views.publisher_edit, name='publisher_edit'),

    # Publisher dashboard (publisher role)
    path('dashboard/publisher/', views.publisher_dashboard, name='publisher_dashboard'),

    # Search
    path('search/', views.search_articles, name='search_articles'),

    # RSS
    path('feed/', BurstArticleFeed(), name='article_feed'),

    # API
    path('api/', include('news.api_urls')),
]
