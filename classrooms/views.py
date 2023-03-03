from django.shortcuts import render
from .forms import ClassCreationForm


def classrooms(request):
    form = ClassCreationForm()
    context = {'form': form}
    return render(request, 'classrooms/classrooms.html', context=context)