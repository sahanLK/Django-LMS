import datetime
import os.path
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, CreateView, DetailView, UpdateView,
                                  DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import AssignmentCreationForm, AssignmentSubmitForm, AssignmentGradeForm, ClassroomCreateForm
from .models import Classroom, Post, Assignment, Submission
from . import view_funcs as vf
from users.models import Lecturer, Student
from main.models import Department


class ClassroomListView(LoginRequiredMixin, ListView):
    model = Classroom
    template_name = "classrooms/class-list.html"
    context_object_name = 'class_rooms'

    def get_queryset(self):
        """
        This method is used to filter the objects that going to be used in this view.
        By default, all the objects will be used in the model.
        :return:
        """
        role = self.request.user.role

        if role == "student":
            return self.request.user.student.classroom_set.all()
        elif role == "lecturer":
            return self.request.user.lecturer.classroom_set.all()


class ClassroomDetailView(LoginRequiredMixin, DetailView):
    """
    Inherited from Generic class based view (DetailView).
    """

    model = Classroom
    template_name = "classrooms/class-detail.html"
    context_object_name = 'class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.get_object()
        context['assignments'] = classroom.assignment_set.all()
        context['lecturers'] = classroom.lecturers.all()
        context['students'] = classroom.students.all()
        context['events'] = self.get_events()
        context['posts'] = self.get_posts()
        return context

    def get_posts(self):
        posts = self.get_object().post_set.all()
        return posts

    def get_events(self):
        # role = self.request.user.role
        #
        # if role == 'student':
        #     assignments = self.get_object().assignment_set.all()    # All the assignments in this class
        #     # All the assignment submissions related to this class
        #     submissions = Submission.objects.filter(
        #         assignment__classroom=self.get_object(),
        #     )
        # if role == 'lecturer':
        pass


class ClassroomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Inherited from Generic class based view (CreateView).
    """

    model = Classroom
    template_name = "classrooms/class-create.html"
    context_object_name = "classroom"
    form_class = ClassroomCreateForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        print(form_kwargs)
        return form_kwargs

    # def get_form_class(self):
    #     form = ClassroomCreateForm
    #     # Allow only enrolled departments to see for current lecturer
    #     print(form.department.choices)
    #     return form

    def form_valid(self, form):
        # Modifying the form instance with required fields.
        # This can also be done by modifying <form.instance>
        classroom = form.save(commit=False)
        classroom.owner = self.request.user.profile
        classroom.save()
        classroom.lecturers.add(self.request.user.profile)  # Add class creator to lecturers list by default
        self.__add_students(classroom)
        return redirect('classrooms')

    @staticmethod
    def __add_students(classroom):
        """
        Accepts classroom instance and add all the students relevant to this
        classroom based on this classroom's department
        :param classroom:
        :return:
        """
        department = classroom.department
        students = Student.objects.filter(department=department)
        for stu in students:
            classroom.students.add(stu)

    def test_func(self):
        """
        Creating a classroom only allowed for a lecturer
        :return:
        """
        if self.request.user.role == "lecturer":
            return True
        return False


class ClassroomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Inherited from Generic class based view (UpdateView).
    """

    model = Classroom
    template_name = "classrooms/class-update.html"
    context_object_name = 'classroom'
    fields = ['name', 'lecturers', 'description']

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

    def test_func(self):
        """
        Updating a classroom only allowed for the class owner. Can only be a lecturer.
        :return:
        """
        if self.request.user.role == 'lecturer':
            if self.request.user.lecturer == self.get_object().owner:
                return True
        return False

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['pk']})


class ClassroomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Inherited from Generic class based view (DeleteView).
    """
    model = Classroom
    template_name = "classrooms/class-delete.html"
    context_object_name = 'classroom'
    success_url = reverse_lazy('classrooms')

    def test_func(self):
        """
        Deleting a classroom is only allowed for classroom owner. Can only be a lecturer.
        :return:
        """
        if self.request.user.role == 'lecturer':
            if self.request.user.lecturer == self.get_object().owner:
                return True
        return False


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    template_name = "classrooms/post-create.html"
    context_object_name = "post"
    fields = ['title', 'content']

    def form_valid(self, form):
        # Updating other required fields of the form, modifying the form instance.
        form.instance.owner = self.request.user.profile
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['class_pk']).first()
        form.instance.date_pub = datetime.datetime.now()
        form.instance.date_last_mod = datetime.datetime.now()
        return super().form_valid(form)

    def test_func(self):
        """
        Updating a classroom only allowed for the class owner. Can only be a lecturer.
        :return:
        """
        if self.request.user.role == 'lecturer':
            return True
        return False

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "classrooms/post-detail.html"
    context_object_name = "post"


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "classrooms/post-update.html"
    context_object_name = "post"
    fields = ('title', 'content')

    def get_success_url(self):
        return reverse('post-details', kwargs={
            'class_pk': self.kwargs['class_pk'], 'pk': self.kwargs['pk']})

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.date_modified = datetime.datetime.now()
        return obj

    def test_func(self):
        """
        Updating posts only allowed for the post author. Can be a lecturer or a student.
        :return:
        """
        if self.request.user.profile == self.get_object().owner:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "classrooms/post-delete.html"
    context_object_name = "post"

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})

    def test_func(self):
        """
        Deleting posts only allowed for the post author. Can be a lecturer or a student.
        :return:
        """
        if self.request.user.profile == self.get_object().owner:
            return True
        return False


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentCreationForm
    template_name = "classrooms/assignment-create.html"
    context_object_name = 'assignment'

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['class_pk']).first()
        form.instance.date_pub = datetime.datetime.now()
        form.instance.date_last_mod = datetime.datetime.now()
        # grade field has a default value. so it is not here
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})

    def test_func(self):
        """
        Creating assignments only allowed for lecturers
        :return:
        """
        if self.request.user.role == 'lecturer':
            return True
        return False


class AssignmentListView(ListView):
    model = Assignment
    template_name = "classrooms/assignments-list.html"
    context_object_name = "assignments"

    def get_queryset(self):
        page_type = self.kwargs['type'].lower()
        user = self.request.user

        # if user.role == 'student':
        #     if page_type == 'pending':
        #         assignments = Assignment.objects.filter()


class StudentListView(ListView):
    model = Student
    template_name = "classrooms/students-list.html"
    context_object_name = "students"

    def get_queryset(self):
        user = self.request.user.profile

        if isinstance(user, Student):
            department = user.department
            fellows = department.student_set.all()
            return fellows

        elif isinstance(user, Lecturer):
            # All the enrolled departments
            depts = user.departments.all()
            all_students = set()

            for dep in depts:
                for stu in dep.students:
                    all_students.add(stu)
            return all_students


def assignment_detail_view(request, **kwargs):  # Consider using update view
    class_pk: str = kwargs['class_pk']
    assignment_pk: str = kwargs['pk']
    assignment: Assignment = Assignment.objects.get(pk=assignment_pk)
    classroom: Classroom = assignment.classroom

    # Uniqueness of <assignment submission object> should depend on [classroom, assignment and student].
    # Only in that case, correct previous submission objects will be detected
    submission = None
    if request.user.role == 'student':
        submission = Submission.objects.filter(
            assignment=assignment,
            owner=request.user.profile,
        ).first()

    if request.method == 'POST':
        form = AssignmentSubmitForm(
            request.POST, request.FILES, instance=submission if submission else None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.date_submitted = datetime.datetime.now()
            obj.assignment = assignment
            obj.classroom = classroom
            obj.profile = vf.get_user_profile(request.user)
            obj.marked_done = True
            obj.save()
            return redirect('assignment-details', class_pk=class_pk, pk=assignment_pk)
    else:
        form = AssignmentSubmitForm(request.POST, request.FILES)

    if submission:
        # Set submission status
        if submission.date_sub >= submission.assignment.date_due:
            submission.status = "Turned in Late"
        else:
            submission.status = "Turned In"

        # Set a user-friendly name attribute for the file
        file_name = submission.file.name
        submission.file_name = f"... {os.path.basename(file_name)[-28:]}"

    context = {
        'form': form,
        'class': classroom,
        'assignment': assignment,
        'submitted': True if submission else False,
        'submission': submission,
    }
    return render(request, "classrooms/assignment-detail.html", context=context)


def assignment_unsubmit_view(request, **kwargs):
    class_pk: str = kwargs['class_pk']
    assignment_pk: str = kwargs['pk']

    classroom: Classroom = Classroom.objects.filter(pk=class_pk).first()
    assignment: Assignment = Assignment.objects.filter(pk=assignment_pk).first()

    submission: Submission = Submission.objects.filter(
        classroom=classroom,
        assignment=assignment,
        profile=vf.get_user_profile(request.user),
    ).first()
    # Delete the submitted file
    submission.delete()     # Delete the record
    return redirect('assignment-details', class_pk=class_pk, pk=assignment_pk)


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    template_name = "classrooms/assignment-update.html"
    context_object_name = "assignment"
    form_class = AssignmentCreationForm

    def test_func(self):
        """
        Assignment update only allowed for the author of the assignment.
        :return:
        """
        if self.request.user.profile == self.get_object().owner:
            return True
        return False

    def get_success_url(self):
        return reverse('assignment-details', kwargs={
            'class_pk': self.kwargs['class_pk'],
            'pk': self.kwargs['pk']})


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    template_name = "classrooms/assignment-delete.html"
    context_object_name = "assignment"

    def get_success_url(self):
        return reverse("class-details", kwargs={'pk': self.kwargs['class_pk']})

    def test_func(self):
        """
        Assignment delete only allowed for the author of the assignment.
        :return:
        """
        if self.request.user.profile == self.get_object().owner:
            return True
        return False


def assignment_submissions_view(request, **kwargs):
    """
    This view should only be visible to lecturers.
    Lecturer can grade the students work from here.
    :param request:
    :return:
    """
    class_pk = kwargs['class_pk']
    assign_pk = kwargs['pk']
    assignment: Assignment = Assignment.objects.get(pk=assign_pk)

    if request.method == 'POST':
        profile = Student.objects.get(pk=request.POST['u_profile_id'])
        obj = Submission.objects.get(
            assignment=assignment,
            profile=profile,
        )
        form = AssignmentGradeForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.grade = request.POST['grade']
            obj.save()
            return redirect('submit-details', class_pk=class_pk, pk=assign_pk)

    # All the student profiles who submitted the current assignment
    submissions = [sub for sub in Submission.objects.filter(
        classroom=vf.get_class(kwargs['class_pk']),
        assignment=assignment,
    )]
    for sub in submissions:
        sub.form = AssignmentGradeForm(instance=sub)

    stu_profiles = vf.get_stu_profiles(kwargs['class_pk'])
    submitted_user_profiles = [sub.profile for sub in submissions]    # <Profile> objects of submitted students

    # Non-submitted students
    non_submitted = set()
    for stu_profile in stu_profiles:
        if stu_profile not in submitted_user_profiles:
            non_submitted.add(stu_profile)

    context = {
        'assignment': assignment,
        'submissions': submissions,
        'non_submitted': non_submitted,
    }
    return render(request, "classrooms/submission-details.html", context=context)


