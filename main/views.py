from django.shortcuts import render, redirect
from .forms import AdminMessageForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Department
from users.models import CustomizedUser, Student, Lecturer


def home(request):
    if request.method == 'POST':
        # Submitting Admin message form
        form = AdminMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "main/message-sent.html")
    else:
        form = AdminMessageForm()

    # Find the current user's profile instance
    profile = None
    if request.user.is_authenticated:
        user = CustomizedUser.objects.get(pk=request.user.pk)
        # profile = Profile.objects.get(user=user)

    context = {'form': form, 'profile': profile}
    return render(request, "main/home.html", context=context)


@login_required
def department_enroll(request, dept_pk, **kwargs):
    if request.user.role == 'lecturer':
        department = Department.objects.get(pk=dept_pk)
        request.user.profile.departments.add(department)
        messages.success(request, "Enroll successful !")
    elif request.user.role == 'student':
        messages.warning(request, "Only lecturers are allowed")
    else:
        messages.error(request, "Unknown error occurred")
    return redirect('departments')


@login_required
def department_leave(request, dept_pk, **kwargs):
    if request.user.role == 'lecturer':
        department = Department.objects.get(pk=dept_pk)
        request.user.profile.departments.remove(department)
        messages.success(request, "Leave successful !")
    elif request.user.role == 'student':
        messages.warning(request, "Only lecturers are allowed")
    else:
        messages.error(request, "Unknown error occurred")
    return redirect('departments')

