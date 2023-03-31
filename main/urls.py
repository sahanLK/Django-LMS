from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('department/<str:dept_pk>/enroll', views.department_enroll, name='dept-enroll'),
    path('department/<str:dept_pk>/leave', views.department_leave, name='dept-leave'),
]