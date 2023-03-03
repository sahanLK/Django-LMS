from django.urls import path
from . import views


urlpatterns = [
    path('classrooms/', views.classrooms, name='classrooms'),
]
