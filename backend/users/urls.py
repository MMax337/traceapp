from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register
from . import api_views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('api/auth/register/', api_views.register_user, name='api-register'),
    path('api/auth/login/', api_views.login_user, name='api-login'),
    path('api/auth/logout/', api_views.logout_user, name='api-logout'),
]
