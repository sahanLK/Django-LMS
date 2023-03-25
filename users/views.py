from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import UserUpdateForm, UserRegisterForm, ProfileUpdateForm
from django.views.generic import ListView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomizedUser, Batch, Department, Profile


def register(request):
    # If admin has not created at lease one batch and department,
    # registrations are not allowed
    if len(Batch.objects.all()) == 0 or len(Department.objects.all()) == 0:
        print("Registrations are not accepting")
        return render(request, "users/no-registrations.html")

    # If logged-in user tried to navigate to the register route, refirect them to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST, request.FILES)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f"Account creates for {u_form.cleaned_data['email']}")
            return redirect('login')
    else:
        u_form = UserRegisterForm()

    context = {'u_form': u_form}
    return render(request, "users/register.html", context=context)


@login_required
def profile_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "profile Updated")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, "users/profile.html", context={'u_form': u_form, 'p_form': p_form})


"""
================================
ADMIN VIEWS
================================
"""


class UsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomizedUser
    template_name = "users/admin/users.html"
    context_object_name = "profiles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lecturers'] = [prof for prof in Profile.objects.filter(role='Lecturer')]
        context['students'] = [prof for prof in Profile.objects.filter(role='Student')]
        return context

    def test_func(self):
        if self.request.user.is_superuser:
            return True


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomizedUser
    template_name = "users/admin/user-delete.html"
    success_url = reverse_lazy('system-users')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
