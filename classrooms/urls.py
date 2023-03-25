from django.urls import path
from . import views


urlpatterns = [
    path('classrooms/', views.ClassroomListView.as_view(), name='classrooms'),
    path('classroom/create/new/', views.ClassroomCreateView.as_view(), name='class-create'),
    path('classroom/<str:pk>/', views.ClassroomDetailView.as_view(), name='class-details'),
    path('classroom/<str:pk>/edit/', views.ClassroomUpdateView.as_view(), name='class-update'),
    path('classroom/<str:pk>/delete/', views.ClassroomDeleteView.as_view(), name='class-delete'),
    path('classroom/<str:class_pk>/post/create-new/', views.PostCreateView.as_view(), name='post-new'),
    path('classroom/<str:class_pk>/post/<str:pk>/', views.PostDetailView.as_view(), name='post-details'),
    path('classroom/<str:class_pk>/post/<str:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('classroom/<str:class_pk>/post/<str:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('classroom/<str:class_pk>/assignment/create-new/',
         views.AssignmentCreateView.as_view(), name='assignment-new'),
    path('classroom/<str:class_pk>/assignment/<str:pk>/',
         views.assignment_detail_view, name='assignment-details'),
    path('classroom/<str:class_pk>/assignment/<str:pk>/update/',
         views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('classroom/<str:class_pk>/assignment/<str:pk>/delete/',
         views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('classroom/<str:class_pk>/assignment/<str:pk>/unsubmit/'
         '', views.assignment_unsubmit_view, name='assignment-unsubmit'),
    path('classroom/<str:class_pk>/assignment/<str:pk>/submissions/',
         views.assignment_submissions_view, name='submit-details'),
    path('assignments/all/<str:type>/', views.AssignmentListView.as_view(), name='assignments-list'),
    path('students/all/', views.StudentListView.as_view(), name='students-list'),
]
