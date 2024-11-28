from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'publish_date', 'created_at')
    list_filter = ('status', 'category', 'tags')
    search_fields = ('title', 'author__username')






# from django.contrib import admin
# from .models import Article

# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author_name', 'category', 'status', 'publish_date', 'created_at')
#     list_filter = ('status', 'category')
#     search_fields = ('title', 'content')
#     actions = ['approve_articles', 'reject_articles', 'publish_articles']

#     def approve_articles(self, request, queryset):
#         queryset.update(status='Review')

#     def reject_articles(self, request, queryset):
#         queryset.update(status='Rejected')

#     def publish_articles(self, request, queryset):
#         queryset.update(status='Published')

# admin.site.register(Article, ArticleAdmin)
