from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('events-today/', views.today_events, name='events-today'),

]