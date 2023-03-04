from django.urls import path
from . import views


urlpatterns = [
    path('classrooms/', views.classrooms, name='classrooms'),
    path('classroom/detail/<str:pk>/', views.ClassroomDetailView.as_view(), name='class-info'),
    path('classroom/update/<str:pk>/', views.ClassroomUpdateView.as_view(), name='class-update'),
]
