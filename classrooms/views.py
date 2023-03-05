from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (ListView,
                                  CreateView,
                                  DetailView,
                                  UpdateView,
                                  DeleteView)
from .models import Classroom


class ClassListView(ListView):
    model = Classroom
    template_name = "classrooms/class-list.html"
    context_object_name = 'class_rooms'


class ClassroomDetailView(DetailView):
    """
    Inherited from Generic class based view (DetailView).
    """
    model = Classroom
    template_name = "classrooms/class-info.html"
    context_object_name = 'class_details'


class ClassCreateView(CreateView):
    """
    Inherited from Generic class based view (CreateView).
    """
    model = Classroom
    template_name = "classrooms/class-create.html"
    context_object_name = "classroom"
    fields = ['name', 'subtitle_1', 'subtitle_2', 'description']

    def form_valid(self, form):
        review = form.save(commit=False)
        review.owner = self.request.user
        review.save()
        return redirect('classrooms')


class ClassroomUpdateView(UpdateView):
    """
    Inherited from Generic class based view (UpdateView).
    """
    model = Classroom
    template_name = "classrooms/class-update.html"
    context_object_name = 'classroom'
    fields = ['name', 'subtitle_1', 'subtitle_2', 'description']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClassroomDeleteView(DeleteView):
    """
    Inherited from Generic class based view (DeleteView).
    """
    model = Classroom
    template_name = "classrooms/class-delete.html"
    context_object_name = 'classroom'
    success_url = reverse_lazy('classrooms')
