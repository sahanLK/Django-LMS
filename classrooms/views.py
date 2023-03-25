import datetime
import os.path

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, CreateView, DetailView, UpdateView,
                                  DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import AssignmentCreationForm, AssignmentSubmitForm, AssignmentGradeForm
from .models import Classroom, Post, Assignment, SubmittedAssignment
from . import view_funcs as vf
from users.models import Profile


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
        role = self.request.user.profile.role
        if role == "Student":
            classes = []
            dept = self.request.user.profile.department
            for classroom in Classroom.objects.all():
                if classroom.owner.profile.department == dept:
                    classes.append(classroom)

        if role == "Lecturer":
            classes = Classroom.objects.filter(owner=self.request.user)
        return classes


class ClassroomDetailView(LoginRequiredMixin, DetailView):
    """
    Inherited from Generic class based view (DetailView).
    """

    model = Classroom
    template_name = "classrooms/class-detail.html"
    context_object_name = 'class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = self.get_assignments()
        context['lecturers'] = vf.get_lec_profiles(self.kwargs['pk'])
        context['students'] = vf.get_stu_profiles(self.kwargs['pk'])
        context['events'] = self.get_pending_assignments(recent=True)
        context['posts'] = self.get_posts()
        return context

    def get_posts(self):
        posts = Post.objects.filter(classroom=vf.get_class(self.kwargs['pk'])).order_by('-date_posted')
        return posts

    def get_assignments(self):
        """
        Get all the assignments in the class
        :return:
        """
        assignments = Assignment.objects.filter(
            classroom=vf.get_class(self.kwargs['pk'])).order_by('-date_posted')
        submitted = self.get_user_submitted_assignments()
        pending = self.get_pending_assignments(recent=False)

        # Set the assignment status for a student
        if self.request.user.profile.role == 'Student':
            for assignment in assignments:
                if assignment in submitted:
                    assignment.status = "Done"
                elif assignment in pending:
                    assignment.status = "Pending"
                else:
                    assignment.status = "Not Detected"

        else:  # Set the assignment status for a Lecturer
            all_assignments = [sub.assignment for sub in SubmittedAssignment.objects.filter(
                classroom=vf.get_class(self.kwargs['pk']))]
            for assignment in assignments:
                done = all_assignments.count(assignment)
                no_of_stu = len(vf.get_stu_profiles(self.kwargs['pk']))

                if int(done) == int(no_of_stu):
                    assignment.status = "All Done"
                else:
                    no_of_stu = len(vf.get_stu_profiles(self.kwargs['pk']))
                    assignment.status = f"{done} / {no_of_stu}"
        return assignments

    def get_user_submitted_assignments(self):
        """
        Get all the assignments submitted by the current user.
        :return:
        """
        # All the submissions done by the current user to current viewing classroom
        submissions = SubmittedAssignment.objects.filter(
            classroom=vf.get_class(self.kwargs['pk']),
            profile=vf.get_user_profile(self.request.user),
        )
        # All the completed assignments
        submitted = [sub.assignment for sub in submissions]
        return submitted

    def get_pending_assignments(self, recent: bool):
        """
        :param recent: If True, only the assignments that has due date within next 14 days will be returned.
        :return:
        """
        today = datetime.datetime.now()
        year, month, day = today.year, today.month, today.day

        if recent:
            assignments = [
                assign for assign in Assignment.objects.filter(
                    classroom=vf.get_class(self.kwargs['pk']),
                    date_due__year=year,
                    date_due__month=month,
                    date_due__day__gte=day,
                    date_due__day__lte=day + 14,
                ).order_by('date_due')
            ]
        else:
            assignments = [assign for assign in Assignment.objects.filter(
                classroom=vf.get_class(self.kwargs['pk']))]

        not_done = []
        submitted = self.get_user_submitted_assignments()    # All the completed assignments

        for assignment in assignments:
            if assignment not in submitted:
                not_done.append(assignment)

        for assignment in not_done:
            due = assignment.date_due
            d_year, d_month, d_day = due.year, due.month, due.day

            if d_year == year and d_month == month and d_day == day:
                assignment.date_due = 'Today'
        return not_done


class ClassroomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Inherited from Generic class based view (CreateView).
    """

    model = Classroom
    template_name = "classrooms/class-create.html"
    context_object_name = "classroom"
    fields = ['name', 'subtitle']

    def form_valid(self, form):
        # Modifying the form instance with required fields.
        # This can also be done by modifying <form.instance>
        review = form.save(commit=False)
        review.owner = self.request.user
        review.save()
        return redirect('classrooms')

    def test_func(self):
        """
        Creating a classroom only allowed for a lecturer
        :return:
        """
        if self.request.user.profile.role == "Lecturer":
            return True
        return False


class ClassroomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Inherited from Generic class based view (UpdateView).
    """

    model = Classroom
    template_name = "classrooms/class-update.html"
    context_object_name = 'classroom'
    fields = ['name', 'subtitle']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Updating a classroom only allowed for the class owner. Can only be a lecturer.
        :return:
        """
        if self.request.user == self.get_object().owner:
            if self.request.user.profile.role == 'Lecturer':
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
        classroom = self.get_object()
        if self.request.user == classroom.owner:
            if self.request.user.profile.role == "Lecturer":
                return True
        return False


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "classrooms/post-create.html"
    context_object_name = "post"
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
        if self.request.user == self.get_object().owner:
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
        if self.request.user == self.get_object().owner:
            return True
        return False


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentCreationForm
    template_name = "classrooms/assignment-create.html"
    context_object_name = 'assignment'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.classroom = Classroom.objects.filter(pk=self.kwargs['class_pk']).first()
        form.instance.date_posted = datetime.datetime.now()
        form.instance.date_modified = datetime.datetime.now()
        # grade field has a default value. so it is not here
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('class-details', kwargs={'pk': self.kwargs['class_pk']})

    def test_func(self):
        """
        Creating assignments only allowed for lecturers
        :return:
        """
        if self.request.user.profile.role == 'Lecturer':
            return True
        return False


class AssignmentListView(ListView):
    model = Assignment
    template_name = "classrooms/assignments-list.html"
    context_object_name = "assignments"

    def get_queryset(self):
        page_type = self.kwargs['type']
        my_prof = vf.get_user_profile(self.request.user)

        if my_prof.role == 'Student':
            if page_type == 'pending':
                pending = set()
                for assign in Assignment.objects.all():
                    # Get assignment owner profile
                    owner_prof = vf.get_user_profile(assign.owner)
                    if owner_prof.department == my_prof.department:
                        pending.add(assign)
                return pending
        elif my_prof.role == 'Lecturer':
            return ["This is for a lecturer"]
        else:
            print("User role unidentified!")


class StudentListView(ListView):
    model = Profile
    template_name = "classrooms/students-list.html"
    context_object_name = "students"


def assignment_detail_view(request, **kwargs):  # Consider using update view
    class_pk: str = kwargs['class_pk']
    assignment_pk: str = kwargs['pk']
    classroom: Classroom = Classroom.objects.filter(pk=class_pk).first()
    assignment: Assignment = Assignment.objects.filter(pk=assignment_pk).first()

    # Uniqueness of <assignment submission object> should depend on [classroom, assignment and student].
    # Only in that case, correct previous submission objects will be detected
    submission: SubmittedAssignment = SubmittedAssignment.objects.filter(
        classroom=classroom,
        assignment=assignment,
        profile=vf.get_user_profile(request.user),
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
        if submission.date_submitted >= submission.assignment.date_due:
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

    submission: SubmittedAssignment = SubmittedAssignment.objects.filter(
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
        if self.request.user == self.get_object().owner:
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
        if self.request.user == self.get_object().owner:
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
        profile = Profile.objects.get(pk=request.POST['u_profile_id'])
        obj = SubmittedAssignment.objects.get(
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
    submissions = [sub for sub in SubmittedAssignment.objects.filter(
        classroom=vf.get_class(kwargs['class_pk']),
        assignment=assignment,
    )]
    for sub in submissions:
        sub.form = AssignmentGradeForm(instance=sub)

    stu_profiles: Profile = vf.get_stu_profiles(kwargs['class_pk'])
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
