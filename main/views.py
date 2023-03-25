from django.shortcuts import render
from .forms import AdminMessageForm
from django.contrib import messages
from users.models import CustomizedUser, Profile


def home(request):
    if request.method == 'POST':
        print(request.POST)
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
        profile = Profile.objects.get(user=user)

    context = {'form': form, 'profile': profile}
    return render(request, "main/home.html", context=context)
