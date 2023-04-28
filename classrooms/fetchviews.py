"""
THESE VIEWS ARE ONLY ACCESSED BY AJAX

This file contains some of non-important data fetching views
"""
from .models import Quiz
from django.http import JsonResponse


def quiz_start_time_view(request, **kwargs):
    quiz = Quiz.objects.get(pk=kwargs['quiz_pk'])
    countdown = f"{quiz.start}"
    return JsonResponse({'countdown': countdown})

