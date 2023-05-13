import json
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import (
    AssignmentCreationForm,
    AssignmentSubmitForm,
    AssignmentGradeForm,
    ClassroomCreateForm,
    ClassroomUpdateForm,
    MeetingCreationForm,
    AssignmentUpdateForm,
    QuizUpdateForm,
)
from django.contrib.auth.decorators import user_passes_test, login_required
from django.template.defaultfilters import slugify
from .models import (
    Classroom,
    Post,
    Assignment,
    Submission,
    SubmissionFile,
    Quiz,
    QuizQuestion,
    QuizQuestionAnswer,
    Meeting, QuizStudentResponseQuestion, QuizStudentResponse, QuizStudentResponseQuestionAnswer
)
from users.models import Lecturer, Student
from main.funcs import (
    is_lecturer,
    is_student,
    get_naive_dt,
    local_to_utc_aware,
    local_to_utc_naive,
    utc_to_local_aware,
    utc_to_local_naive,
    get_naive_dt)
from django.http import JsonResponse
from http.client import OK
from .forms import MeetingUpdateForm, QuizCreateForm
from main.funcs import local_to_utc_aware


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

        assignments = classroom.assignment_set.all()
        meetings = classroom.meeting_set.all()
        quizzes = classroom.quiz_set.all()
        work = set(a for a in assignments)
        work.update(set(m for m in meetings))
        work.update(set(q for q in quizzes))

        # Sort the classwork by date_posted using BUBBLE-SORT ALGORITHM
        def bubble_sort(array):
            n = len(array)

            for i in range(n):
                already_sorted = True
                for j in range(n - i - 1):
                    if array[j].date_created < array[j + 1].date_created:
                        array[j], array[j + 1] = array[j + 1], array[j]
                        already_sorted = False
                if already_sorted:
                    break
            return array

        context['class_work'] = bubble_sort(list(work))
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
        dept_field.help_text = 'only your enrolled departments will be displayed here.'
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
    fields = ('title', 'content')

    def form_valid(self, form):
        # Updating other required fields of the form, modifying the form instance.
        form.instance.owner = self.request.user.profile
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['pk']).first()
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
    template_name = "classrooms/posts/post-details.html"
    context_object_name = "post"


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "classrooms/posts/post-update.html"
    context_object_name = "post"
    fields = ('title', 'content')

    def get_success_url(self):
        return reverse('post-details', kwargs={
            'class_pk': self.kwargs['class_pk'], 'pk': self.kwargs['pk']})

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
        form.instance._date_due = local_to_utc_aware(form.instance._date_due)
        # grade field has a default value. so it is not here

        # Manually validating form for checking assignment title is unique for a particular classroom
        cls = Classroom.objects.get(pk=form.instance.classroom.pk)
        title = form.instance.title
        exists = cls.assignment_set.filter(title=title).first()
        if exists:
            form.add_error('title', 'Assignment with this title already exists in this classroom')
            return self.form_invalid(form)
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


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    template_name = "classrooms/assignments/assignment-update.html"
    context_object_name = "assignment"
    form_class = AssignmentUpdateForm

    def get_form_kwargs(self):
        # Converting UTC _date_due into local time. UTC should not show up in update form
        kwargs = super().get_form_kwargs()
        instance = kwargs.get('instance')
        instance._date_due = utc_to_local_naive(instance._date_due)
        kwargs.update({'instance': instance})
        return kwargs

    def form_valid(self, form):
        form.instance._date_due = local_to_utc_aware(form.instance._date_due)   # Convert to UTC when updating

        # Manually validating form for checking assignment title is unique for a particular classroom
        assignment = self.get_object()
        exists = assignment.classroom.assignment_set.filter(
            title=form.instance.title).exclude(pk=assignment.pk)
        if exists:
            form.add_error('title', 'Assignment with this title already exists in this classroom')
            return self.form_invalid(form)
        return super().form_valid(form)

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
            'class_name': slugify(self.kwargs['class_name']),
            'pk': self.kwargs['pk']})


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
            sub.file = None     # Files will be saved with <SubmissionFile> model
            sub.save()

            # Saving all the selected files
            for f in request.FILES.getlist('file'):
                file = SubmissionFile(submission=sub, file=f)
                file.save()

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
                    class_name=slugify(assignment.classroom.name),
                    pk=assignment.pk)


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
                            class_name=slugify(assignment.classroom.name),
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
                            class_name=slugify(assignment.classroom.name),
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
                    class_name=slugify(assignment.classroom.name),
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
                    class_name=slugify(assignment.classroom.name),
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
        form.instance._start = local_to_utc_aware(form.instance._start)
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
    template_name = 'classrooms/meetings/meeting-update.html'
    form_class = MeetingUpdateForm
    context_object_name = 'meeting'

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False

    def get_success_url(self):
        meeting = self.get_object()
        cls_name = slugify(meeting.classroom.name)
        return reverse('meeting-details', kwargs={
            'class_name': cls_name, 'pk': meeting.pk})


class MeetingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meeting
    template_name = 'classrooms/meetings/meeting-delete.html'
    context_object_name = 'meeting'

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False

    def get_success_url(self):
        cls_pk = self.get_object().classroom.pk
        return reverse('class-details', kwargs={'pk': cls_pk})


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    template_name = 'classrooms/meetings/meeting-details.html'
    context_object_name = 'meeting'


"""
=============================
    QUIZ VIEWS
=============================
"""


class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    template_name = 'classrooms/quizzes/quiz-create.html'

    def get_form_class(self):
        """
        Setting some help texts
        :return:
        """
        form = QuizCreateForm
        accept_after_field = form.base_fields.get('accept_after_expired')
        duration_field = form.base_fields.get('duration')

        accept_after_field.help_text = 'Will allow students to submit' \
                                       ' responses even after time exceeded'
        duration_field.help_text = 'Time in minutes'
        return form

    def form_valid(self, form):
        form.instance.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        form.instance.owner = self.request.user.profile
        form.instance._start = local_to_utc_aware(form.instance._start)

        # Manually validate for quizzes with same title
        exists = Quiz.objects.filter(title=form.instance.title)
        if exists:
            form.add_error('title', 'Quiz with this title already exists in this classroom.')
            return self.form_invalid(form)

        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False

    def get_success_url(self):
        quiz = self.get_form_kwargs().get('instance')
        return reverse('quiz-questions', kwargs={
            'class_name': slugify(quiz.classroom.name),
            'quiz_pk': quiz.pk,
        })


class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'classrooms/quizzes/quiz-list.html'
    context_object_name = 'quizzes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_type = self.kwargs['type']

        color = 'secondary'
        if quiz_type == 'today':
            color = 'danger'
        elif quiz_type == 'upcoming':
            color = 'warning'
        elif quiz_type == 'previous':
            color = 'success'
        context['color'] = color
        return context

    def get_queryset(self):
        quiz_type = self.kwargs['type']
        prof = self.request.user.profile

        if isinstance(prof, Student):
            prof: Student

            if quiz_type == 'today':
                return prof.get_today_quizzes()
            elif quiz_type == 'upcoming':
                return prof.get_upcoming_quizzes()
            elif quiz_type == 'missing':
                return prof.get_missing_quizzes()
            elif quiz_type == 'completed':
                return prof.get_completed_quizzes()

        elif isinstance(prof, Lecturer):
            prof: Lecturer

            if quiz_type == 'today':
                return prof.get_today_quizzes()
            elif quiz_type == 'upcoming':
                return prof.get_upcoming_quizzes()
            elif quiz_type == 'previous':
                return prof.get_previous_quizzes()


class QuizUpdateView(UpdateView):
    model = Quiz
    template_name = 'classrooms/quizzes/quiz-update.html'
    context_object_name = 'quiz'
    form_class = QuizUpdateForm

    def get_form_kwargs(self):
        # Converting UTC _date_due into local time. UTC should not show up in update form
        kwargs = super().get_form_kwargs()
        instance = kwargs.get('instance')
        instance._start = utc_to_local_naive(instance._start)
        kwargs.update({'instance': instance})
        return kwargs

    def form_valid(self, form):
        form.instance._start = local_to_utc_aware(form.instance._start)

        # Manually check if quiz title is not using by another quiz except this one.
        exists = Quiz.objects.filter(
            title=form.instance.title).exclude(pk=self.get_object().pk)
        if exists:
            form.add_error('title', 'Quiz with this title already exists in the classroom.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        quiz = self.get_object()
        cls_name = slugify(quiz.classroom.name)
        return reverse('quiz-details', kwargs={
            'class_name': cls_name, 'pk': quiz.pk})


class QuizDeleteView(DeleteView):
    model = Quiz
    template_name = 'classrooms/quizzes/quiz-delete.html'
    context_object_name = 'quiz'

    def get_success_url(self):
        quiz = self.get_object()
        return reverse('class-details', kwargs={
            'pk': quiz.classroom.pk,})


class QuizDetailView(DetailView, LoginRequiredMixin):
    model = Quiz
    context_object_name = 'quiz'

    def get_template_names(self):
        quiz = self.get_object()
        if quiz.live and not self.response and self.request.user.is_student:
            return 'classrooms/quizzes/parts/live.html'
        else:
            return 'classrooms/quizzes/quiz-details.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        context = super().get_context_data(**kwargs)
        context['time_counter'] = quiz.start
        context['response'] = self.response
        return context

    @property
    def response(self):
        user = self.request.user
        if user.is_student:
            response = QuizStudentResponse.objects.filter(
                owner=user.profile,
                quiz=self.get_object(),).first()
            return response


"""
=============================
    QUIZ QUESTIONS VIEWS
=============================
"""


def _bubble_sort(array):
    array = [i for i in array]
    n = len(array)

    for i in range(n):  # 3
        already_sorted = True

        for j in range(n - i - 1):
            if array[j].number > array[j + 1].number:
                array[j], array[j + 1] = array[j + 1], array[j]
                already_sorted = False
        if already_sorted:
            break
    return array


def quiz_questions_and_answers_view(
        request, class_name, quiz_pk, **kwargs):
    """
    ONLY FOR LECTURERS  (CALLED BY AJAX)

    CREATING AND UPDATING QUIZ ANSWERS BOTH DONE IN THIS VIEW.
    WHENEVER NEED TO CREATE OR UPDATE QUESTIONS AND ANSWERS,
    ALL PREVIOUS QUESTIONS ANS ANSWERS GETS DELETED AND
    QUIZ WILL BE REGENERATED COMPLETELY.
    """
    if not request.user.is_lecturer:
        return HttpResponseNotAllowed([])

    quiz = Quiz.objects.get(pk=quiz_pk)

    if request.method == 'POST':
        # If quiz has responses or starting time exceeded, no edits allowed
        if len(quiz.quizstudentresponse_set.all()) > 0:
            return JsonResponse({'msg': 'responses-available'})

        # Delete all the existing question and answers
        for record in quiz.quizquestion_set.all():
            record.delete()

        # Recreate all questions and answers with the latest datasets
        q_objects = json.loads(request.POST.get('dom'))

        for q_obj in q_objects.get('dom'):
            # Creating <QuizQuestion> object
            question = q_obj['question']
            q_id = question['question-id']
            q_text = question['text'].strip(' ')
            q_question = QuizQuestion(
                quiz=quiz,
                number=q_id,
                question=q_text,
            )
            q_question.save()

            # Creating answers related for above question
            for ans in q_obj['answers']:
                q_answer = QuizQuestionAnswer(
                    question=q_question,
                    letter=ans['letter'],
                    answer=ans['text'].strip(' '),
                    correct=True if ans['correct'] == 'true' else False,
                )
                q_answer.save()

    context = {'quiz': quiz}
    return render(request, 'classrooms/quizzes/quiz-questions.html', context)


def quiz_live_view(request, **kwargs):
    """
    ONLY FOR STUDENTS (CALLED BY AJAX)
    """
    if not request.user.is_student:
        return HttpResponseNotAllowed([])

    quiz = Quiz.objects.get(pk=kwargs['quiz_pk'])
    context = {'quiz': quiz}

    if request.method == 'POST':    # Student submitting a response
        # Not allowed making more than 1 response for same quiz
        if not len(request.user.profile.quizstudentresponse_set.filter(quiz=quiz)) > 0:
            # creating <QuizStudentResponse> object
            response = QuizStudentResponse(
                quiz=quiz,
                owner=request.user.profile,
            )
            response.save()

            # Creating questions and answers related to the response
            q_objects = json.loads(request.POST.get('dom'))

            for q_obj in q_objects.get('dom'):
                # Creating <QuizStudentResponseQuestion> object
                question = q_obj['question']
                q_id = question['question-id']
                question = QuizQuestion.objects.get(number=q_id)
                q_res_question = QuizStudentResponseQuestion(
                    response=response,
                    question=question,
                )
                q_res_question.save()

                # Creating answers related for above question
                for ans in q_obj['answers']:
                    # Save answers that only selected as True by student
                    if ans['correct'] == 'true':
                        # detect the correct answer
                        answer_letter = ans['letter']
                        answer = question.quizquestionanswer_set.get(letter=answer_letter)

                        q_res_answer = QuizStudentResponseQuestionAnswer(
                            response_question=q_res_question,
                            answer=answer,
                        )
                        q_res_answer.save()

            """generate score for the response"""

            _all_questions = quiz.quizquestion_set.filter()

            # Finding all the correct answers of the actual quiz
            _all_correct_ans = set()
            _all_incorrect_ans = set()
            for question in _all_questions:
                for a in question.quizquestionanswer_set.all():
                    if a.correct:
                        _all_correct_ans.add(a)
                    else:
                        _all_incorrect_ans.add(a)

            # Finding all the correct and incorrect answers that student has marked
            correct_stu = set()
            incorrect_stu = set()
            all_res_questions = response.quizstudentresponsequestion_set.all()
            for q in all_res_questions:

                # <quizstudentresponsequestionanswer_set> only contains the
                # answers that student selected as correct
                for ans in q.quizstudentresponsequestionanswer_set.all():
                    if ans.answer.correct:
                        correct_stu.add(ans)
                    else:
                        incorrect_stu.add(ans)

            correct_actual = len(_all_correct_ans)
            correct_stu = len(correct_stu)

            try:
                correct_score = (correct_stu/correct_actual)*100
                incorrect_score = len(incorrect_stu)
                score = correct_score - (incorrect_score * 0.1)
            except ZeroDivisionError:   # No actual correct answers for the quiz
                if len(incorrect_stu) == 0:
                    score = 100
                else:
                    score = 0

            score = 0 if score < 0 else score
            response.score = round(score, 2)
            response.save()

        else:
            print("You already have a response")
            # return JsonResponse({'what_happened': 'Already responded'})

    return render(request, 'classrooms/quizzes/parts/live.html', context)


def quiz_stu_response_view(request, **kwargs):
    """
    The view that displays the student response anytime.
    """

    quiz = Quiz.objects.get(pk=kwargs['quiz_pk'])
    response = request.user.profile.quizstudentresponse_set.filter(quiz=quiz).first()

    # all the response question. Usually contains all the
    # questions in the quiz.
    # This is used for instead of quiz directly, because from these
    # objects, student's answers can be directly accessed.
    res_questions = response.quizstudentresponsequestion_set.all()

    all_answers = set()
    for q in res_questions:
        for question in q.quizstudentresponsequestionanswer_set.all():
            all_answers.add(question.answer)

    context = {
        'quiz': quiz,
        'res_questions': res_questions,
        'all_answers': all_answers,
        'response': response
    }
    return render(request, 'classrooms/quizzes/quiz-stu-response.html', context)


class QuizResultsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = QuizStudentResponse
    context_object_name = 'responses'
    template_name = 'classrooms/quizzes/parts/results.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = Quiz.objects.get(pk=self.kwargs['quiz_pk'])
        return context

    def test_func(self):
        if self.request.user.is_lecturer:
            return True
        return False

