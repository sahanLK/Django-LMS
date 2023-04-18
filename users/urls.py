from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name="users/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name="users/logout.html"), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="users/password-reset.html"), name='password-reset'),

    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('departments/all/', views.DepartmentListView.as_view(), name='departments'),
    path('department/<str:dept_pk>/enroll', views.department_enroll, name='dept-enroll'),
    path('department/<str:dept_pk>/leave', views.department_leave, name='dept-leave'),
    path('user/statistics/', views.statistics_view, name='statistics'),
    path('people/', views.people_view, name='people'),
]
