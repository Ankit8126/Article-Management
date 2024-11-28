from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.validators import MinLengthValidator
import datetime

# from django.contrib import admin
# from .models import Article



class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('blocked', 'Blocked'),
    ]

    CATEGORY_CHOICES = [
        ('News', 'News'),
        ('Opinion', 'Opinion'),
        ('Feature', 'Feature'),
    ]

    TAG_CHOICES = [
        ('Politics', 'Politics'),
        ('Sports', 'Sports'),
        ('Tech', 'Tech'),
        ('Health', 'Health'),
    ]

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(10, message="Title must be at least 10 characters long.")]
    )
    subtitle = models.CharField(max_length=255, blank=True, verbose_name=_("Subtitle"))
    content = models.TextField(verbose_name=_("Content"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles")
    email = models.EmailField(verbose_name=_("Author Email"))
    image = models.ImageField(upload_to="articles/images/", blank=True, null=True)
    rejection_count = models.IntegerField(default=0)
    tags = models.CharField(
        max_length=50,
        choices=TAG_CHOICES,
        verbose_name=_("Tags"),
        default='politics'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name=_("Category")
    )
    publish_date = models.DateField(verbose_name=_("Publish Date"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Status")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles'
    
    # terms_agreed = models.BooleanField(default=False)
    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-created_at"]

    def clean(self):
        if self.publish_date and self.publish_date <= now().date():
            raise ValidationError(_("Publish date must be a future date."))

    def __str__(self):
        return self.title

    # @admin.register(Article)
    # class ArticleAdmin(admin.ModelAdmin):
    #     list_display = ('title', 'author', 'status', 'publish_date', 'created_at')
    #     list_filter = ('status', 'category', 'tags')
    #     search_fields = ('title', 'author__username')



    

    # Optional: Tag Model for Filtering (if needed)
# class Tag(models.Model):
#     name = models.CharField(max_length=50)
#     articles = models.ManyToManyField(Article, related_name='tags')

#     def __str__(self):
#         return self.name
