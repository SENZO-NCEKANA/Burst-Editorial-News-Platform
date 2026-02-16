"""
REST API views for news application.
"""

from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Article, Publisher, Category, Newsletter, Subscription
from .serializers import (
    ArticleSerializer, ArticleListSerializer, PublisherSerializer,
    PublisherDetailSerializer, CategorySerializer, NewsletterSerializer,
    SubscriptionSerializer
)


class ArticleListAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating articles.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter articles based on user role and subscriptions.
        """
        user = self.request.user

        if user.is_reader():
            # Readers see only published articles from their subscriptions
            subscribed_publishers = Subscription.objects.filter(
                user=user, publisher__isnull=False
            ).values_list('publisher', flat=True)

            subscribed_journalists = Subscription.objects.filter(
                user=user, journalist__isnull=False
            ).values_list('journalist', flat=True)

            return Article.objects.filter(
                Q(status='published') & (
                    Q(publisher__in=subscribed_publishers) |
                    Q(author__in=subscribed_journalists)
                )
            ).select_related('author', 'publisher', 'category')

        elif user.is_journalist():
            # Journalists see their own articles
            return Article.objects.filter(author=user)

        elif user.is_editor():
            # Editors see articles from their publishers and pending articles
            return Article.objects.filter(
                Q(publisher__editors=user) | Q(status='pending')
            )

        return Article.objects.none()

    def perform_create(self, serializer):
        """
        Set the author to the current user.
        """
        serializer.save(author=self.request.user)


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting articles.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter articles based on user role.
        """
        user = self.request.user

        if user.is_reader():
            return Article.objects.filter(status='published')
        elif user.is_journalist():
            return Article.objects.filter(author=user)
        elif user.is_editor():
            return Article.objects.filter(
                Q(publisher__editors=user) | Q(status='pending')
            )

        return Article.objects.none()


class PublisherListAPIView(generics.ListAPIView):
    """
    API view for listing publishers.
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublisherDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating a publisher.
    Restricted to staff or the publisher owner.
    """
    serializer_class = PublisherDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Publisher.objects.all()
        return Publisher.objects.filter(owner=user)

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_staff and serializer.instance.owner != user:
            raise PermissionDenied(
                'Only the owner or staff can update this publisher.'
            )
        serializer.save()


class CategoryListAPIView(generics.ListAPIView):
    """
    API view for listing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class NewsletterListAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating newsletters.
    """
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter newsletters based on user role.
        """
        user = self.request.user

        if user.is_reader():
            # Readers see newsletters from their subscriptions
            subscribed_publishers = Subscription.objects.filter(
                user=user, publisher__isnull=False
            ).values_list('publisher', flat=True)

            subscribed_journalists = Subscription.objects.filter(
                user=user, journalist__isnull=False
            ).values_list('journalist', flat=True)

            return Newsletter.objects.filter(
                Q(publisher__in=subscribed_publishers) |
                Q(author__in=subscribed_journalists)
            )

        elif user.is_journalist():
            return Newsletter.objects.filter(author=user)

        return Newsletter.objects.none()

    def perform_create(self, serializer):
        """
        Set the author to the current user.
        """
        serializer.save(author=self.request.user)


class SubscriptionListAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return subscriptions for the current user.
        """
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the user to the current user.
        """
        serializer.save(user=self.request.user)


class SubscriptionDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    API view for retrieving and deleting subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return subscriptions for the current user.
        """
        return Subscription.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_article_api(request, pk):
    """
    API endpoint for approving articles (editors only).
    """
    if not request.user.is_editor():
        return Response(
            {'error': 'Only editors can approve articles'},
            status=status.HTTP_403_FORBIDDEN
        )

    article = get_object_or_404(Article, pk=pk)

    # Editors may only approve articles from their publisher
    if (article.publisher and
            not article.publisher.editors.filter(pk=request.user.pk).exists()):
        return Response(
            {'error': 'You can only approve articles from your publisher.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if article.is_approved:
        return Response(
            {'error': 'Article is already approved'},
            status=status.HTTP_400_BAD_REQUEST
        )

    article.approve(request.user)

    return Response(
        {'message': 'Article approved successfully'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_subscriptions_api(request):
    """
    API endpoint for getting user's subscribed content.
    """
    user = request.user

    if not user.is_reader():
        return Response(
            {'error': 'Only readers can view subscriptions'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get subscribed publishers
    publisher_subscriptions = Subscription.objects.filter(
        user=user, publisher__isnull=False
    ).select_related('publisher')

    # Get subscribed journalists
    journalist_subscriptions = Subscription.objects.filter(
        user=user, journalist__isnull=False
    ).select_related('journalist')

    # Get articles from subscriptions
    subscribed_publishers = publisher_subscriptions.values_list(
        'publisher', flat=True)
    subscribed_journalists = journalist_subscriptions.values_list(
        'journalist', flat=True)

    articles = Article.objects.filter(
        Q(publisher__in=subscribed_publishers) |
        Q(author__in=subscribed_journalists),
        status='published'
    ).select_related('author', 'publisher', 'category')

    # Serialize data
    publisher_data = PublisherSerializer(
        [sub.publisher for sub in publisher_subscriptions], many=True
    ).data

    journalist_data = [
        {
            'id': sub.journalist.id,
            'username': sub.journalist.username,
            'email': sub.journalist.email
        }
        for sub in journalist_subscriptions
    ]

    article_data = ArticleListSerializer(articles, many=True).data

    return Response({
        'publishers': publisher_data,
        'journalists': journalist_data,
        'articles': article_data
    })
