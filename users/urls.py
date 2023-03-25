from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="users/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="users/logout.html"), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.UsersListView.as_view(), name='system-users'),
    path('user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]
