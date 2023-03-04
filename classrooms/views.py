from django.shortcuts import render, redirect
from .forms import ClassCreationForm
from django.views.generic import ListView, DetailView, FormView, UpdateView
from .models import Classroom


# class ClassroomsView(FormView):
#     model = Classroom
#     template_name = "classrooms/classrooms.html"
#     context_object_name = 'classroom'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context[]


def classrooms(request):
    if request.method == "POST":
        form = ClassCreationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect('classrooms')
    else:
        form = ClassCreationForm()

    class_rooms = Classroom.objects.all()
    context = {
        'form': form,
        'class_rooms': class_rooms,
    }
    return render(request, 'classrooms/classrooms.html', context=context)


class ClassroomDetailView(DetailView):
    model = Classroom
    template_name = "classrooms/class-info.html"
    context_object_name = 'class_details'


class ClassroomUpdateView(UpdateView):
    model = Classroom
    template_name = "classrooms/class-update.html"
    context_object_name = 'classroom'
    fields = ['name', 'subtitle_1', 'subtitle_2', 'description']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)