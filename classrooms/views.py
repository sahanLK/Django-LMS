import datetime
import os.path
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, CreateView, DetailView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import AssignmentCreationForm, AssignmentSubmitForm, AssignmentGradeForm, ClassroomCreateForm, \
    ClassroomUpdateForm, QuizCreateForm, MeetingCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Classroom, Post, Assignment, Submission, Quiz, QuizQuestion, QuizQuestionAnswer, Meeting
from users.models import Lecturer, Student
from main.funcs import is_lecturer, is_student, d_t
from .forms import MeetingUpdateForm, QuizCreateForm


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
            return self.request.user.student.department.classroom_set.all()
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
        context['students'] = classroom.department.student_set.all()
        context['events'] = None
        context['posts'] = self.get_posts()
        return context

    def get_posts(self):
        posts = self.get_object().post_set.all()
        return posts


class ClassroomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Inherited from Generic class based view (CreateView).
    """

    model = Classroom
    template_name = "classrooms/class-create.html"
    context_object_name = "classroom"

    def get_form_class(self):
        form = ClassroomCreateForm
        # Allow lecturer create classrooms only on enrolled departments.
        enrolled = [(dept.pk, dept) for dept in self.request.user.profile.departments.all()]
        dept_field = form.base_fields.get('department')
        dept_field.choices = enrolled
        return form

    def form_valid(self, form):
        # Modifying the form instance with required fields.
        # This can also be done by modifying <form.instance>
        classroom = form.save(commit=False)
        classroom.owner = self.request.user.profile
        classroom.save()

        # Classroom owner(creator), by default should also be a lecturer of that class.
        # Otherwise, the classroom will not be shown to the creator.
        classroom.lecturers.add(self.request.user.profile)
        messages.success(self.request, "Classroom Created !")
        return redirect('classrooms')

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

    def get_form_class(self):
        form = ClassroomUpdateForm
        lecs_field = form.base_fields.get('lecturers')

        # Allow to update the classroom without selecting any lecturers, because
        # classroom owner will always be added in <form_valid> method.
        lecs_field.required = False
        # Don't show the lecturer himself in lecturers list, when updating the classroom.
        lecs_field.queryset = lecs_field.queryset.exclude(user=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile  # set classroom owner
        form.save()

        """
        After saving the form with above line, only the currently selected 
        lecturer will be saved. So, add the owner again as a lecturer manually.
        Classroom always need it's owner.
        """
        self.request.user.profile.classroom_set.add(self.get_object())
        messages.success(self.request, "Classroom Updated !")
        return HttpResponseRedirect(self.get_success_url())

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

    def form_valid(self, form):
        messages.success(self.request, "Classroom Deleted !")
        return super(ClassroomDeleteView, self).form_valid(form)


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    template_name = "classrooms/posts/post-create.html"
    context_object_name = "post"
    fields = ['title', 'content']

    def form_valid(self, form):
        # Updating other required fields of the form, modifying the form instance.
        form.instance.owner = self.request.user.profile
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['pk']).first()
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
        return reverse('class-details', kwargs={'pk': self.kwargs['pk']})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "classrooms/posts/post-detail.html"
    context_object_name = "post"


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "classrooms/posts/post-update.html"
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
    template_name = "classrooms/posts/post-delete.html"
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


class StudentListView(ListView):
    model = Student
    template_name = "classrooms/students-list.html"
    context_object_name = "students"

    def get_queryset(self):
        profile = self.request.user.profile

        if isinstance(profile, Student):
            return self.__get_stu_fellows(profile)
        elif isinstance(profile, Lecturer):
            return self.__get_students(profile)

    @staticmethod
    def __get_students(lecturer: Lecturer):
        """
        ONLY FOR LECTURERS
        Returns a list of all the students from all the departments that
        the given lecturer is enrolled in.
        :param lecturer:
        :return:
        """
        # All the enrolled departments
        depts = lecturer.departments.all()
        all_students = set()

        for dep in depts:
            for stu in dep.student_set.all():
                all_students.add(stu)
        return all_students

    @staticmethod
    def __get_stu_fellows(student: Student):
        """
        ONLY FOR STUDENTS
        Returns a list of fellow students for a student
        :return:
        """
        department = student.department
        fellows = department.student_set.all()
        return fellows


"""
=============================
    ASSIGNMENT VIEWS
=============================
"""


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentCreationForm
    template_name = "classrooms/assignments/assignment-create.html"
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


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = "classrooms/assignments/assignments-list.html"
    context_object_name = "assignments"

    page_type = None

    def get_queryset(self):
        profile = self.request.user.profile
        page_type = self.kwargs['type'].lower()
        self.page_type = page_type

        if isinstance(profile, Student):
            if page_type == 'pending':
                return profile.get_pending_assignments()
            elif page_type == 'missing':
                return profile.get_missing_assignments()
            elif page_type == 'completed':
                return profile.get_all_completed_assignments()

        elif isinstance(profile, Lecturer):
            if page_type == 'all':
                return profile.get_all_assignments()
            elif page_type == 'ongoing':
                return profile.get_ongoing_assignments()
            elif page_type == 'pending-review':
                return profile.get_pending_review_assignments()
            elif page_type == 'reviewed':
                return profile.get_reviewed_assignments()

    def get_context_data(self, **kwargs):
        """
        This is overridden here only for design purposes.
        Assignment list will be colored according to the page_type.
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        t = self.page_type

        # Generating bootstrap color code for different pages
        if t == 'completed' or t == 'reviewed':
            color = 'success'
        elif t == 'pending' or t == 'pending-review':
            color = 'warning'
        elif t == 'missing':
            color = 'danger'
        else:
            color = 'secondary'
        context['color'] = color
        return context


def assignment_detail_view(request, **kwargs):  # Consider using update view
    assignment: Assignment = Assignment.objects.get(pk=kwargs['pk'])

    submission = None
    if request.user.role == 'student':
        submission = Submission.objects.filter(
            assignment=assignment,
            owner=request.user.profile,
        ).first()

    if request.method == 'POST':
        # Student is trying to make a submission for this assignment.
        form = AssignmentSubmitForm(
            request.POST, request.FILES, instance=submission if submission else None)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.owner = request.user.profile

            from django.utils import timezone
            n = timezone.now()
            sub.date_sub = n
            sub.save()
            messages.success(request, "Submission Successful !")
            return redirect('assignment-details',
                            class_name=assignment.classroom.name.replace(' ', '-'),
                            pk=assignment.pk)
        else:
            messages.error(request, "Submission Failed !")
    else:
        form = AssignmentSubmitForm()

    context = {
        'form': form,
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, "classrooms/assignments/assignment-detail.html", context=context)


def assignment_unsubmit_view(request, **kwargs):
    assignment: Assignment = Assignment.objects.get(pk=kwargs['pk'])

    submission: Submission = Submission.objects.get(
        assignment=assignment,
        owner=request.user.profile,)
    submission.delete()     # Delete the submission
    return redirect('assignment-details',
                    class_name=assignment.classroom.name.replace(' ', '-'),
                    pk=assignment.pk)


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    template_name = "classrooms/assignments/assignment-update.html"
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
            'class_name': self.kwargs['class_name'],
            'pk': self.kwargs['pk']})


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    template_name = "classrooms/assignments/assignment-delete.html"
    context_object_name = "assignment"

    def get_success_url(self):
        cls_pk = self.get_object().classroom.pk
        return reverse("class-details", kwargs={'pk': cls_pk})

    def test_func(self):
        """
        Assignment delete only allowed for the author of the assignment.
        :return:
        """
        if self.request.user.profile == self.get_object().owner:
            return True
        return False


@user_passes_test(is_lecturer)
@login_required
def assignment_submissions_view(request, **kwargs):
    """
    This view should only be visible to lecturers.
    Lecturer can grade the students work from here.
    :param request:
    :return:
    """
    assignment: Assignment = Assignment.objects.get(pk=kwargs['assignment_pk'])

    if request.method == 'POST':    # Lecturer trying to grade the assignment
        # To determine which user profile is going to be graded,
        # SubmissionGrade form uses a hidden input field with the
        # value of <Student> object primary key.
        requesting_prof_pk = request.POST.get('u_profile_id')

        # If requesting submission profile id is
        # not by hidden input field, do not go ahead
        if not requesting_prof_pk:
            messages.error(request, "Student id could not be confirmed")
            return redirect('submit-details',
                            class_name=assignment.classroom.name.replace(' ', '-'),
                            assignment_pk=assignment.pk)

        requesting_prof = Student.objects.get(pk=requesting_prof_pk)
        obj = Submission.objects.get(
            assignment=assignment,
            owner=requesting_prof,
        )
        form = AssignmentGradeForm(request.POST, instance=obj)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.grade = request.POST.get('grade')
            obj.save()
            return redirect('submit-details',
                            class_name=assignment.classroom.name.replace(' ', '-'),
                            assignment_pk=assignment.pk)
    else:
        submissions = assignment.submission_set.all()

        # Add grading form attribute to each submission object
        for sub in submissions:
            sub.form = AssignmentGradeForm(instance=sub)

        # All the non-submitted students
        submitted_profiles = [sub.owner for sub in submissions]
        non_submitted = [prof for prof in assignment.classroom.department.student_set.all()
                         if prof not in submitted_profiles]

        context = {
            'assignment': assignment,
            'submissions': submissions,
            'non_submitted': non_submitted,
        }
        return render(request, "classrooms/assignments/submission-details.html", context=context)


@user_passes_test(is_lecturer)
@login_required
def assignment_complete_review_view(request, assignment_pk, **kwargs):
    assignment = Assignment.objects.get(pk=assignment_pk)
    try:
        assignment.review_complete = True
        assignment.save()
        messages.success(request, "Review completed !")
    except Exception as e:
        messages.error(request, "Something went wrong !")
    return redirect('submit-details',
                    class_name=assignment.classroom.name.replace(' ', '-'),
                    assignment_pk=assignment.pk)


@user_passes_test(is_lecturer)
@login_required
def assignment_undo_complete_review_view(request, assignment_pk, **kwargs):
    try:
        assignment = Assignment.objects.get(pk=assignment_pk)
        assignment.review_complete = False
        assignment.save()
        messages.success(request, "Review restarted !")
    except Exception as e:
        messages.error(request, "Something went wrong !")
    return redirect('submit-details',
                    class_name=assignment.classroom.name.replace(' ', '-'),
                    assignment_pk=assignment.pk)


"""
=============================
    MEETING VIEWS
=============================
"""


class MeetingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Meeting
    template_name = "classrooms/meetings/meeting-create.html"

    def get_form_class(self):
        """
        Without classroom the invalid form submission displays an
        error page. To prevent this, classroom field should be added with
        default value and in disables state. Then, when an invalid submission
        occurs, a nice error message will be displayed instead of error page.
        :return:
        """
        form = MeetingCreationForm
        cls_field = form.base_fields.get('classroom')
        cls_field.queryset = Classroom.objects.filter(pk=self.kwargs['pk']).all()
        cls_field.initial = cls_field.queryset.first()
        cls_field.disabled = True
        return form

    def form_valid(self, form):
        # form.instance.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy('class-details', kwargs={'pk': self.kwargs['pk']})


class MeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'classrooms/meetings/meetings-list.html'
    context_object_name = 'meetings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meet_type = self.kwargs['type']

        color = 'secondary'
        if meet_type == 'today':
            color = 'danger'
        elif meet_type == 'upcoming':
            color = 'warning'
        elif meet_type == 'previous':
            color = 'success'
        context['color'] = color
        return context

    def get_queryset(self):
        meet_type = self.kwargs['type']
        prof = self.request.user.profile

        if isinstance(prof, Student):
            if meet_type == 'today':
                return prof.get_today_meetings()
            elif meet_type == 'upcoming':
                return prof.get_upcoming_meetings()
            elif meet_type == 'previous':
                return prof.get_prev_meetings()

        elif isinstance(prof, Lecturer):
            if meet_type == 'today':
                return prof.get_today_meetings()
            elif meet_type == 'upcoming':
                return prof.get_upcoming_meetings()
            elif meet_type == 'previous':
                return prof.get_prev_meetings()


class MeetingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Meeting
    template_name = 'classrooms/meetings/meeting-create.html'
    form_class = MeetingUpdateForm
    context_object_name = 'meeting'

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False


class MeetingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meeting
    template_name = 'classrooms/meetings/meeting-delete.html'
    context_object_name = 'meeting'

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False


class MeetingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Meeting
    template_name = 'classrooms/meetings/meeting-details.html'
    context_object_name = 'meeting'

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False


"""
=============================
    QUIZ VIEWS
=============================
"""


class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    template_name = 'classrooms/quizzes/quiz-create.html'
    form_class = QuizCreateForm

    def form_valid(self, form):
        form.instance.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False


class QuizUpdateView(UpdateView):
    pass


class QuizDeleteView(DeleteView):
    pass


class QuizDetailView(DetailView):
    pass


