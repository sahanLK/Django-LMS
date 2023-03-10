import datetime
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views import View
from users.models import Profile  # No error because similar to django Shell import
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, CreateView, DetailView, UpdateView,
                                  DeleteView, FormView)
from .forms import AssignmentCreationForm, AssignmentSubmitForm
from .models import Classroom, Post, Assignment


"""
CLASSROOM
===============================================================
"""


class ClassroomListView(ListView):
    model = Classroom
    template_name = "classrooms/class-list.html"
    context_object_name = 'class_rooms'
    queryset = Classroom.objects.filter()

    def get_queryset(self):
        """
        This method is used to filter the objects that going to be used in this view.
        By default, all the objects will be used in the model.
        :return:
        """
        classes = Classroom.objects.filter(owner=self.request.user)
        return classes


class ClassroomDetailView(DetailView):
    """
    Inherited from Generic class based view (DetailView).
    """
    model = Classroom
    template_name = "classrooms/class-detail.html"
    context_object_name = 'class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['posts'] = self.get_posts()
        context['assignments'] = self.get_assignments()
        context['lecturers'] = self.get_lecturers()
        context['students'] = self.get_students()
        context['events'] = self.get_upcoming_events()

        # stream section contains all the posts and assignments according to date posted
        context['posts'] = Post.objects.all().order_by('-date_posted')
        return context

    def get_class(self):
        """
        Get the current requesting class instance by primary key
        :return:
        """
        cls = Classroom.objects.filter(pk=self.kwargs['pk']).first()
        return cls

    def get_posts(self):
        posts = Post.objects.filter(classroom=self.get_class())
        return posts

    def get_assignments(self):
        assignments = Assignment.objects.filter(classroom=self.get_class()).order_by('-date_posted')
        return assignments

    def get_lecturers(self):
        owner = self.get_class().owner
        return [owner]

    def get_students(self):
        """
        Students are filtered based on the department of the class owner's department.
        :return:
        """
        owner_dept = self.get_class().owner.profile.department
        students = Profile.objects.filter(department=owner_dept, role='Student')
        return students

    def get_upcoming_events(self):
        """
        Get recent events within one-week time period from the current date.
        :return:
        """
        today = datetime.datetime.now()
        year, month, day = today.year, today.month, today.day
        assignments = [assign for assign in Assignment.objects.filter(classroom=self.get_class(),
                                                                      date_due__year=year,
                                                                      date_due__month=month,
                                                                      date_due__day__gte=day,
                                                                      date_due__day__lte=day+14,
                                                                      )]
        for assignment in assignments:
            due = assignment.date_due
            d_year, d_month, d_day = due.year, due.month, due.day

            if d_year == year and d_month == month and d_day == day:
                assignment.date_due = 'today'
        return assignments


class ClassroomCreateView(CreateView):
    """
    Inherited from Generic class based view (CreateView).
    """
    model = Classroom
    template_name = "classrooms/class-create.html"
    context_object_name = "classroom"
    fields = ['name', 'subtitle_1', 'subtitle_2', 'description']

    def form_valid(self, form):
        # Modifying the form instance with required fields.
        # This can also be done by modifying <form.instance>
        review = form.save(commit=False)
        review.owner = self.request.user
        review.save()
        print(self.args)
        return redirect('classes')


class ClassroomUpdateView(UpdateView):
    """
    Inherited from Generic class based view (UpdateView).
    """
    model = Classroom
    template_name = "classrooms/class-update.html"
    context_object_name = 'classroom'
    fields = ['name', 'subtitle_1', 'description']

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


"""
POST
===============================================================
"""


class PostCreateView(CreateView):
    model = Post
    template_name = "classrooms/post-create.html"
    context_object_name = "classroom"
    fields = ['title', 'content']

    def form_valid(self, form):
        # Updating other required fields of the form, modifying the form instance.
        form.instance.owner = self.request.user
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['class_pk']).first()
        form.instance.date_posted = datetime.datetime.now()
        form.instance.date_modified = datetime.datetime.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})


class PostDetailView(DetailView):
    model = Post
    template_name = "classrooms/post-detail.html"
    context_object_name = "post"


class PostUpdateView(UpdateView):
    model = Post
    template_name = "classrooms/post-update.html"
    context_object_name = "post"
    fields = ('title', 'content')

    def get_success_url(self):
        return reverse('post-detail', kwargs={'class_pk': self.kwargs['class_pk'], 'pk': self.kwargs['pk']})

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.date_modified = datetime.datetime.now()
        return obj


class PostDeleteView(DeleteView):
    model = Post
    template_name = "classrooms/post-delete.html"
    context_object_name = "post"

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})


"""
ASSIGNMENT
===============================================================
"""


class AssignmentCreateView(CreateView):
    model = Assignment
    form_class = AssignmentCreationForm
    template_name = "classrooms/assignment-create.html"
    context_object_name = 'assignment'
    success_url = reverse_lazy('classrooms')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        print("DDD", self.kwargs['class_pk'])
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['class_pk']).first()
        form.instance.date_posted = datetime.datetime.now()
        form.instance.date_modified = datetime.datetime.now()
        # grade field has a default value. so it is not here
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})


class AssignmentInsideView(DetailView):
    template_name = "classrooms/assignment-detail.html"
    context_object_name = 'assignment'

    def get_queryset(self):
        queryset = Assignment.objects.filter(classroom=self.kwargs['class_pk'])
        return queryset


# def assignment_detail(request, **kwargs):  # Consider using update view
#     class_pk = kwargs['class_pk']
#     assignment_pk = kwargs['pk']
#     classroom = Classroom.objects.filter(pk=class_pk).first()
#     assignment = Assignment.objects.filter(pk=assignment_pk).first()
#
#     if request.method == 'POST':
#         form = AssignmentSubmitForm(request.POST, request.FILES, instance=assignment)
#         if form.is_valid():
#             form.save()
#             return redirect('assignment-detail', kwargs={'class_pk': class_pk, 'pk': assignment_pk})
#
#     else:
#         form = AssignmentSubmitForm()
#
#     context = {
#         'form': form,
#         'class': classroom,
#         'assignment': assignment,
#     }
#     return render(request, "classrooms/assignment-detail.html", context=context)


class AssignmentUpdateView(UpdateView):
    model = Assignment
    template_name = "classrooms/assignment-update.html"
    context_object_name = "assignment"
    fields = ('title', 'content', 'date_due', 'documents')


class AssignmentDeleteView(DeleteView):
    model = Assignment
    template_name = "classrooms/assignment-delete.html"
    context_object_name = "assignment"

    def get_success_url(self):
        return reverse("class-details", kwargs={'pk': self.kwargs['class_pk']})
