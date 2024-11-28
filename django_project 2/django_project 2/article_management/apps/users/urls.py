from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import *
import debug_toolbar

app_name = 'users'


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm',),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('dashboard/', dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('editor-dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('journalist-dashboard/', views.journalist_dashboard, name='journalist_dashboard'),
    # path('default-dashboard/', views.default_dashboard, name='default_dashboard'),
    path('__debug__/', include(debug_toolbar.urls))
]
