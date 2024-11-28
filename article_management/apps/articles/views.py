from rest_framework import viewsets, permissions, filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Article
from .serializers import ArticleSerializer
from apps.articles.models import Article
# from apps.articles.serializers import ArticleSerializer
from .serializers import ArticleSerializer
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ArticleFormPage1, ArticleFormPage2
from rest_framework.filters import SearchFilter
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail

# from .users.permissions import IsAdmin

class IsJournalist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'journalist'

class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'editor'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class ArticleFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=Article.CATEGORY_CHOICES)
    tags = django_filters.ChoiceFilter(choices=Article.TAG_CHOICES)

    class Meta:
        model = Article
        fields = ['category', 'tags']

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'content', 'tags']  # Fields to search by

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []  # Accessible to all
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated & (IsJournalist | IsAdmin)]
        elif self.action in ['approve', 'reject', 'publish']:
            permission_classes = [IsAuthenticated & (IsEditor | IsAdmin)]
        else:
            permission_classes = [IsAdmin]  # Default for admin-only actions
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        article = self.get_object()
        if article.status == 'approved':
            return Response({"detail": "Article is already approved."}, status=400)
        article.status = 'approved'
        article.save()
        return Response({"detail": "Article approved successfully."})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        article = self.get_object()
        article.rejection_count += 1
        article.save()

        if article.rejection_count >= 3:
            article.status = 'blocked'
        else:
            article.status = 'rejected'
        article.save()

        return Response({"detail": f"Article rejected. Rejections: {article.rejection_count}"})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        if article.status != 'approved':
            return Response({"detail": "Article must be approved before publishing."}, status=400)
        article.status = 'published'
        article.save()
        return Response({"detail": "Article published successfully."})

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Article.objects.all()
        return Article.objects.filter(author=user)

    def perform_create(self, serializer):
        # Save the article
        article = serializer.save(author=self.request.user)
        
        # Notify editors
        send_mail(
            subject=f"New Article Submitted: {article.title}",
            message=f"An article titled '{article.title}' has been submitted by {article.author}.",
            from_email='your-email@example.com',
            recipient_list=['ankitk908432@gmail.com'],  # Replace with editor's email
        )

    def perform_update(self, serializer):
        article = serializer.save()
        
        # Notify the journalist when the article is approved/rejected
        if 'status' in serializer.validated_data:  # Assuming 'status' tracks approval/rejection
            status = serializer.validated_data['status']
            send_mail(
                subject=f"Article {article.title} {status}",
                message=f"Your article '{article.title}' has been {status}.",
                from_email='your-email@example.com',
                recipient_list=[article.author.email],
            )

    @action(detail=False, methods=['get'])
    def published(self, request):
        # Only list published articles
        published_articles = Article.objects.filter(status='published')
        serializer = self.get_serializer(published_articles, many=True)
        return Response(serializer.data)



def article_submission_page1(request):
    if request.method == 'POST':
        form = ArticleFormPage1(request.POST)
        if form.is_valid():
            # Store form data in session
            request.session['form_page1'] = form.cleaned_data
            return redirect(reverse('articles:submission_page2'))
    else:
        form = ArticleFormPage1()
    return render(request, 'articles/submission_page1.html', {'form': form})

def article_submission_page2(request):
    if request.method == 'POST':
        form = ArticleFormPage2(request.POST, request.FILES)
        if form.is_valid():
            # Combine data from session and current form
            article_data = {**request.session.get('form_page1', {}), **form.cleaned_data}
            Article.objects.create(**article_data)
            return redirect(reverse('articles:article_list'))
    else:
        form = ArticleFormPage2()
    return render(request, 'articles/submission_page2.html', {'form': form})


# class IsEditorOrAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         # Allow access if user is admin or editor
#         return request.user.is_staff or request.user.groups.filter(name__in=['Editor', 'Admin']).exists()

# class ArticleViewSet(viewsets.ModelViewSet):
#     """
#     A ViewSet for managing Articles with role-based permissions.
#     """
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#     permission_classes = [IsAuthenticated]

#     # Apply filtering and searching
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['title', 'content', 'tags']
#     ordering_fields = ['publish_date', 'created_at']

#     def get_permissions(self):
#         """
#         Set permissions dynamically based on user role and request type.
#         """
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             return [IsEditorOrAdmin()]
#         return super().get_permissions()

#     def perform_create(self, serializer):
#         """
#         Automatically associate the article with the logged-in user.
#         """
#         serializer.save(author=self.request.user)

#     @action(detail=True, methods=['post'], permission_classes=[IsEditorOrAdmin])
#     def approve(self, request, pk=None):
#         """
#         Custom action to approve an article.
#         """
#         article = self.get_object()
#         if article.status == 'pending':
#             article.status = 'approved'
#             article.save()
#             return Response({"message": "Article approved successfully."})
#         return Response({"error": "Only articles in 'pending' status can be approved."})







# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .forms import ArticlePage1Form, ArticlePage2Form

# def article_submission_page1(request):
#     if request.method == "POST":
#         form = ArticlePage1Form(request.POST)
#         if form.is_valid():
#             request.session['page1_data'] = form.cleaned_data
#             return redirect('articles:submission_page2')
#     else:
#         form = ArticlePage1Form()
#     return render(request, 'articles/submission_page1.html', {'form': form})

# def article_submission_page2(request):
#     page1_data = request.session.get('page1_data', None)
#     if not page1_data:
#         return redirect('articles:submission_page1')  # Redirect to Page 1 if no data exists

#     if request.method == "POST":
#         form = ArticlePage2Form(request.POST, request.FILES)
#         if form.is_valid():
#             # Combine data from both pages and create an Article
#             article_data = {**page1_data, **form.cleaned_data}
#             article = Article.objects.create(**article_data)
#             return redirect('articles:submission_success')  # Redirect after saving article
#     else:
#         form = ArticlePage2Form()

#     return render(request, 'articles/submission_page2.html', {'form': form})

# @login_required
# def create_article(request):
#     if request.method == "POST":
#         form_page1 = ArticlePage1Form(request.POST)
#         form_page2 = ArticlePage2Form(request.POST, request.FILES)
#         if form_page1.is_valid() and form_page2.is_valid():
#             # Create article
#             article_data = {**form_page1.cleaned_data, **form_page2.cleaned_data}
#             article_data['author'] = request.user
#             article = Article.objects.create(**article_data)
#             send_mail(
#                 'Article Submitted for Review',
#                 'Your article has been successfully submitted for review.',
#                 'admin@media.com',  # Admin email
#                 [request.user.email],
#             )
#             return redirect('articles:article_list')
#     else:
#         form_page1 = ArticlePage1Form()
#         form_page2 = ArticlePage2Form()

#     return render(request, 'articles/create_article.html', {'form_page1': form_page1, 'form_page2': form_page2})

# @login_required
# def edit_article(request, article_id):
#     article = get_object_or_404(Article, id=article_id)
#     if article.author != request.user and not request.user.is_staff:
#         return HttpResponseForbidden()

#     if request.method == "POST":
#         form_page1 = ArticlePage1Form(request.POST, instance=article)
#         form_page2 = ArticlePage2Form(request.POST, request.FILES, instance=article)
#         if form_page1.is_valid() and form_page2.is_valid():
#             form_page1.save()
#             form_page2.save()
#             return redirect('articles:article_list')
#     else:
#         form_page1 = ArticlePage1Form(instance=article)
#         form_page2 = ArticlePage2Form(instance=article)

#     return render(request, 'articles/edit_article.html', {'form_page1': form_page1, 'form_page2': form_page2, 'article': article})

# @login_required
# def article_list(request):
#     if request.user.is_staff:
#         articles = Article.objects.all()
#     else:
#         articles = Article.objects.filter(author=request.user)
#     return render(request, 'articles/article_list.html', {'articles': articles})

# @login_required
# def approve_article(request, article_id):
#     article = get_object_or_404(Article, id=article_id)
#     if not request.user.is_staff:
#         return HttpResponseForbidden()

#     article.status = 'Review'
#     article.save()

#     # Notify the author
#     send_mail(
#         'Article Approved for Review',
#         f'Your article "{article.title}" has been approved for review.',
#         'admin@media.com',  # Admin email
#         [article.author.email],
#     )

#     return redirect('articles:article_list')

# @login_required
# def reject_article(request, article_id):
#     article = get_object_or_404(Article, id=article_id)
#     if not request.user.is_staff:
#         return HttpResponseForbidden()

#     article.status = 'Rejected'
#     article.save()

#     # Notify the author
#     send_mail(
#         'Article Rejected',
#         f'Your article "{article.title}" has been rejected.',
#         'admin@media.com',  # Admin email
#         [article.author.email],
#     )

#     return redirect('articles:article_list')

# class ArticleViewSet(viewsets.ModelViewSet):
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return Article.objects.all()  # Admin can view all articles
#         return Article.objects.filter(author=user)  # Journalists can view their own articles