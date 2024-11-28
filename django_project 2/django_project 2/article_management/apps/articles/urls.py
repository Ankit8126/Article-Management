from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = router.urls






# from django.urls import include, path
# from . import views
# from rest_framework.routers import DefaultRouter
# from .views import ArticleViewSet

# app_name = 'articles'

# router = DefaultRouter()
# router.register(r'articles', ArticleViewSet)

# urlpatterns = [
#     path('submit/page1/', views.article_submission_page1, name='submission_page1'),
#     path('submit/page2/', views.article_submission_page2, name='submission_page2'),
#     path('api/', include(router.urls)),
#     path('create/', views.create_article, name='create_article'),
#     path('edit/<int:article_id>/', views.edit_article, name='edit_article'),
#     path('list/', views.article_list, name='article_list'),
#     path('approve/<int:article_id>/', views.approve_article, name='approve_article'),
#     path('reject/<int:article_id>/', views.reject_article, name='reject_article'),
#     path('publish/<int:article_id>/', views.publish_article, name='publish_article'),
# ]
