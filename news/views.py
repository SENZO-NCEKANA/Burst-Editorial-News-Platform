"""
Views for news application with role-based access control.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    User, Article, Publisher, Category, Subscription, PasswordResetToken,
    Newsletter
)
from .forms import (
    UserRegistrationForm, ArticleForm, NewsletterForm,
    SubscriptionForm, ArticleApprovalForm, ForgotPasswordForm,
    ResetPasswordForm, PublisherForm, AddTeamMemberForm
)


def staff_required(user):
    """Check if user is staff."""
    return user.is_authenticated and user.is_staff


def page_not_found(request, exception):
    """Custom 404 handler."""
    return render(request, 'news/404.html', status=404)


def server_error(request):
    """Custom 500 handler."""
    return render(request, 'news/500.html', status=500)


def terms(request):
    """Terms of service placeholder."""
    return render(request, 'news/terms.html')


def privacy(request):
    """Privacy policy placeholder."""
    return render(request, 'news/privacy.html')


def home(request):
    """
    Home page displaying recent articles and newsletters, filterable by category and publisher.
    """
    articles = Article.objects.filter(
        status='published'
    ).select_related('author', 'publisher', 'category')

    category = request.GET.get('category', '')
    publisher = request.GET.get('publisher', '')

    if category:
        articles = articles.filter(category__name=category)
    if publisher:
        articles = articles.filter(publisher__name=publisher)

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Recent newsletters (filter by publisher if applied)
    newsletters = Newsletter.objects.all().select_related('author', 'publisher')
    if publisher:
        newsletters = newsletters.filter(publisher__name=publisher)
    newsletters = newsletters.order_by('-created_at')[:5]

    context = {
        'page_obj': page_obj,
        'newsletters': newsletters,
        'categories': Category.objects.all(),
        'publishers': Publisher.objects.all(),
        'current_category': category,
        'current_publisher': publisher,
    }
    return render(request, 'news/home.html', context)


@login_required
@user_passes_test(staff_required)
def publisher_list(request):
    """
    List publishers (staff only).
    """
    publishers = Publisher.objects.all().select_related('owner').order_by('name')
    context = {'publishers': publishers}
    return render(request, 'news/publisher_list.html', context)


@login_required
@user_passes_test(staff_required)
def publisher_create(request):
    """
    Create publisher (staff only).
    """
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher created successfully.')
            return redirect('news:publisher_list')
    else:
        form = PublisherForm()
    return render(request, 'news/publisher_form.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def publisher_edit(request, pk):
    """
    Edit publisher (staff only).
    """
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher updated successfully.')
            return redirect('news:publisher_list')
    else:
        form = PublisherForm(instance=publisher)
    return render(
        request,
        'news/publisher_form.html',
        {'form': form, 'publisher': publisher}
    )


@login_required
def publisher_dashboard(request):
    """
    Dashboard for publisher-role users to manage their publishing house.
    """
    if not request.user.is_publisher():
        messages.error(request, 'Only publishers can access this dashboard.')
        return redirect('news:home')

    publisher = request.user.owned_publishers.first()
    if not publisher:
        messages.warning(
            request,
            'You do not own a publishing house. Contact staff to get assigned.'
        )
        return redirect('news:home')

    add_form = AddTeamMemberForm()
    if request.method == 'POST' and 'add_member' in request.POST:
        add_form = AddTeamMemberForm(request.POST)
        if add_form.is_valid():
            username = add_form.cleaned_data['username']
            role = add_form.cleaned_data['role']
            try:
                user = User.objects.get(username=username)
                if role == 'editor':
                    if user.role != 'editor':
                        messages.error(
                            request,
                            f'{username} is not an editor. They must register '
                            'as an editor first.'
                        )
                    elif publisher.editors.filter(pk=user.pk).exists():
                        messages.warning(request, f'{username} is already an editor.')
                    else:
                        publisher.editors.add(user)
                        messages.success(request, f'Added {username} as editor.')
                else:
                    if user.role != 'journalist':
                        messages.error(
                            request,
                            f'{username} is not a journalist. They must register '
                            'as a journalist first.'
                        )
                    elif publisher.journalists.filter(pk=user.pk).exists():
                        messages.warning(request, f'{username} is already a journalist.')
                    else:
                        publisher.journalists.add(user)
                        messages.success(request, f'Added {username} as journalist.')
            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')
            return redirect('news:publisher_dashboard')

    articles = Article.objects.filter(publisher=publisher).order_by('-created_at')[:10]
    newsletters = Newsletter.objects.filter(publisher=publisher).order_by('-created_at')[:5]
    subscriber_count = Subscription.objects.filter(publisher=publisher).count()

    context = {
        'publisher': publisher,
        'editors': publisher.editors.all(),
        'journalists': publisher.journalists.all(),
        'add_form': add_form,
        'articles': articles,
        'newsletters': newsletters,
        'article_count': Article.objects.filter(publisher=publisher).count(),
        'subscriber_count': subscriber_count,
    }
    return render(request, 'news/publisher_dashboard.html', context)


def register(request):
    """
    User registration view with role selection.
    Supports publisher assignment for editors/journalists and
    publisher creation for publisher role.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = user.role
            publisher = form.cleaned_data.get('publisher')

            if role == 'publisher':
                pub = Publisher.objects.create(
                    name=form.cleaned_data['publisher_name'].strip(),
                    description=form.cleaned_data.get('publisher_description')
                    or '',
                    website=form.cleaned_data.get('publisher_website') or '',
                    owner=user
                )
                messages.success(
                    request,
                    f'Account and publishing house "{pub.name}" created.'
                )
            elif role == 'editor' and publisher:
                publisher.editors.add(user)
                messages.success(
                    request,
                    f'Account created. You are now an editor at {publisher.name}.'
                )
            elif role == 'journalist' and publisher:
                publisher.journalists.add(user)
                messages.success(
                    request,
                    f'Account created. You are now a journalist at {publisher.name}.'
                )
            else:
                messages.success(
                    request,
                    f'Account created successfully for {user.username}.'
                )

            login(request, user)
            return redirect('news:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'news/register.html', {'form': form})


def user_login(request):
    """
    User login view.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('news:home')
            else:
                messages.error(request, 'Invalid password')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')

    return render(request, 'news/login.html')


@login_required
def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('news:home')


@login_required
def article_list(request):
    """
    Article list view with role-based filtering.
    """
    articles = Article.objects.all()

    if request.user.is_reader():
        articles = articles.filter(status='published')
    elif request.user.is_journalist():
        articles = articles.filter(author=request.user)
    elif request.user.is_editor():
        articles = articles.filter(
            Q(publisher__editors=request.user) | Q(status='pending')
        )

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_role': request.user.role,
    }
    return render(request, 'news/article_list.html', context)


@login_required
def article_detail(request, pk):
    """
    Article detail view.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.is_reader() and article.status != 'published':
        messages.error(request, 'This article is not published yet')
        return redirect('news:article_list')

    context = {'article': article}
    return render(request, 'news/article_detail.html', context)


@login_required
def create_article(request):
    """
    Create article view for journalists.
    """
    if not request.user.is_journalist():
        messages.error(request, 'Only journalists can create articles')
        return redirect('news:article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully')
            return redirect('news:article_detail', pk=article.pk)
    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {'form': form})


@login_required
def edit_article(request, pk):
    """
    Edit article view for journalists and editors.
    """
    article = get_object_or_404(Article, pk=pk)

    if not (request.user == article.author or
            request.user.is_editor()):
        messages.error(
            request,
            'You do not have permission to edit this article'
        )
        return redirect('news:article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully')
            return redirect('news:article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)

    context = {'form': form, 'article': article}
    return render(request, 'news/edit_article.html', context)


@login_required
def approve_article(request, pk):
    """
    Article approval view for editors.
    """
    if not request.user.is_editor():
        messages.error(request, 'Only editors can approve articles')
        return redirect('news:article_list')

    article = get_object_or_404(Article, pk=pk)

    # Editors may only approve articles from their publisher
    if (article.publisher and
            not article.publisher.editors.filter(pk=request.user.pk).exists()):
        messages.error(
            request,
            'You can only approve articles from your publisher.'
        )
        return redirect('news:article_list')

    if request.method == 'POST':
        form = ArticleApprovalForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.approve(request.user)
            article.save()
            messages.success(request, 'Article approved successfully')
            return redirect('news:article_detail', pk=article.pk)
    else:
        form = ArticleApprovalForm(instance=article)

    context = {'form': form, 'article': article}
    return render(request, 'news/approve_article.html', context)


@login_required
def subscription_management(request):
    """
    Subscription management view for readers.
    """
    if not request.user.is_reader():
        messages.error(request, 'Only readers can manage subscriptions')
        return redirect('news:home')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user

            # Use get_or_create to handle duplicates gracefully
            if subscription.publisher:
                sub, created = Subscription.objects.get_or_create(
                    user=request.user,
                    publisher=subscription.publisher,
                    defaults={'journalist': None}
                )
                if created:
                    messages.success(
                        request,
                        f'Successfully subscribed to '
                        f'{subscription.publisher.name}'
                    )
                else:
                    messages.warning(
                        request,
                        f'You are already subscribed to '
                        f'{subscription.publisher.name}'
                    )
            elif subscription.journalist:
                sub, created = Subscription.objects.get_or_create(
                    user=request.user,
                    journalist=subscription.journalist,
                    defaults={'publisher': None}
                )
                if created:
                    messages.success(
                        request,
                        f'Successfully subscribed to '
                        f'{subscription.journalist.username}'
                    )
                else:
                    messages.warning(
                        request,
                        f'You are already subscribed to '
                        f'{subscription.journalist.username}'
                    )

            return redirect('news:subscription_management')
    else:
        form = SubscriptionForm()

    subscriptions = Subscription.objects.filter(user=request.user)

    context = {
        'form': form,
        'subscriptions': subscriptions,
    }
    return render(request, 'news/subscription_management.html', context)


@login_required
def delete_subscription(request, pk):
    """
    Delete subscription view.
    """
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)

    if request.method == 'POST':
        subscription.delete()
        messages.success(request, 'Subscription removed successfully')
        return redirect('news:subscription_management')

    context = {'subscription': subscription}
    return render(request, 'news/delete_subscription.html', context)


def newsletter_list(request):
    """
    List newsletters. Journalists see their own; others see recent from subscriptions.
    """
    if request.user.is_authenticated and request.user.is_journalist():
        newsletters = Newsletter.objects.filter(author=request.user).order_by('-created_at')
    elif request.user.is_authenticated and request.user.is_reader():
        subs = Subscription.objects.filter(user=request.user)
        publishers = [s.publisher for s in subs if s.publisher]
        journalists = [s.journalist for s in subs if s.journalist]
        newsletters = Newsletter.objects.filter(
            Q(publisher__in=publishers) | Q(author__in=journalists)
        ).distinct().order_by('-created_at')[:50]
    else:
        newsletters = Newsletter.objects.all().order_by('-created_at')[:20]

    return render(request, 'news/newsletter_list.html', {'newsletters': newsletters})


def newsletter_detail(request, pk):
    """
    View a single newsletter. Public for sharing.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(request, 'news/newsletter_detail.html', {'newsletter': newsletter})


@login_required
def create_newsletter(request):
    """
    Create newsletter view for journalists.
    """
    if not request.user.is_journalist():
        messages.error(request, 'Only journalists can create newsletters')
        return redirect('news:home')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            messages.success(request, 'Newsletter created successfully')
            return redirect('news:newsletter_detail', pk=newsletter.pk)
    else:
        form = NewsletterForm()

    return render(request, 'news/create_newsletter.html', {'form': form})


def search_articles(request):
    """
    Search articles view.
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    publisher = request.GET.get('publisher', '')

    articles = Article.objects.filter(status='published')

    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    if category:
        articles = articles.filter(category__name=category)

    if publisher:
        articles = articles.filter(publisher__name=publisher)

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'categories': Category.objects.all(),
        'publishers': Publisher.objects.all(),
    }
    return render(request, 'news/search_results.html', context)


def forgot_password(request):
    """
    Handle password reset request.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)

                # Generate token for password reset
                import secrets
                token = secrets.token_urlsafe(32)

                # Create password reset token
                PasswordResetToken.objects.create(
                    user=user,
                    token=token
                )

                # Send email with reset link
                from django.core.mail import send_mail
                from django.conf import settings

                reset_url = request.build_absolute_uri(
                    f'/reset-password/{token}/'
                )

                try:
                    send_mail(
                        'Password Reset Request',
                        f'Click the link to reset your password: {reset_url}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                except Exception as e:
                    # Log the error but don't expose it to the user
                    print(f"Email sending failed: {e}")
                    # Still show success message for security

                messages.success(
                    request,
                    'Password reset link sent to your email.'
                )
                return redirect('news:login')

            except User.DoesNotExist:
                messages.error(
                    request,
                    'No account found with that email address.'
                )
    else:
        form = ForgotPasswordForm()

    return render(request, 'news/forgot_password.html', {'form': form})


def reset_password(request, token):
    """
    Handle password reset with token.
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            messages.error(request, 'Invalid or expired reset token.')
            return redirect('news:forgot_password')

        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                reset_token.user.set_password(new_password)
                reset_token.user.save()

                # Mark token as used
                reset_token.is_used = True
                reset_token.save()

                messages.success(
                    request,
                    'Password reset successfully. Please log in.'
                )
                return redirect('news:login')
        else:
            form = ResetPasswordForm()

        return render(
            request,
            'news/reset_password.html',
            {'form': form, 'token': token}
        )

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset token.')
        return redirect('news:forgot_password')
