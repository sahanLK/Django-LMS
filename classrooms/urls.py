from django.urls import path
from . import views


urlpatterns = [
    path('classrooms/', views.ClassListView.as_view(), name='classrooms'),
    path('classroom/create/new/', views.ClassCreateView.as_view(), name='class-create'),
    path('classroom/detail/<str:pk>/', views.ClassroomDetailView.as_view(), name='class-info'),
    path('classroom/<str:pk>/edit/', views.ClassroomUpdateView.as_view(), name='class-update'),
    path('classroom/<str:pk>/delete/', views.ClassroomDeleteView.as_view(), name='class-delete'),
]
