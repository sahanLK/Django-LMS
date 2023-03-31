from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from .forms import (UserRegisterForm, LecturerCreationForm, StudentCreationForm,
                    StudentUpdateForm, LecturerUpdateForm, UserUpdateForm)
from django.views.generic import ListView, DeleteView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from classrooms.models import Classroom


def register(request):
    # If admin has not created at least one batch and department,
    # registrations are not allowed
    if len(Department.objects.all()) == 0:
        print("Registrations are not accepting")
        return render(request, "users/no-registrations.html")

    # If logged-in user tried to navigate to the register route, refirect them to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        lec_create_form = LecturerCreationForm(request.POST)
        stu_create_form = StudentCreationForm(request.POST)

        # Prevent users from submitting both students and lecturer registration forms at once.
        reg_type = request.POST['reg_type'].lower()

        if u_form.is_valid():
            # Create user
            user = u_form.save(commit=False)
            u_form.save()

            if reg_type == 'lecturer':
                if lec_create_form.is_valid():
                    # Make the created user a lecturer
                    lec = lec_create_form.save(commit=False)
                    lec.user = user
                    lec.save()
                    return redirect('login')

            elif reg_type == 'student':
                if stu_create_form.is_valid():
                    # Make the created user a student
                    stu = stu_create_form.save(commit=False)
                    stu.user = user
                    stu.save()

                    # Add the registered student to all the relevant classrooms
                    department = stu.department
                    classrooms = Classroom.objects.filter(department=department)
                    for cls in classrooms:
                        stu.classroom_set.add(cls)
                    return redirect('login')
    else:
        u_form = UserRegisterForm()
        lec_create_form = LecturerCreationForm()
        stu_create_form = StudentCreationForm()

    context = {
        'u_form': u_form,
        'lec_create_form': lec_create_form,
        'stu_create_form': stu_create_form,
    }
    return render(request, "users/register.html", context=context)


@login_required
def profile(request):
    role = request.user.role

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if role == 'student':
            p_form = StudentUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        elif role == 'lecturer':
            p_form = LecturerUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        else:
            # Probably admin
            p_form = None

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "profile Updated")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

        if role == 'student':
            p_form = StudentUpdateForm(instance=request.user.student)
        elif role == 'lecturer':
            p_form = LecturerUpdateForm(instance=request.user.lecturer)
        else:
            p_form = None
    return render(request, "users/profile.html", context={'u_form': u_form, 'p_form': p_form})


class LecturerEnrolledDepartmentsListView(ListView):
    model = Department
    context_object_name = "departments"
    template_name = "classrooms/department-list.html"
