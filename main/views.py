from django.shortcuts import render


def home(request):
    profile = None
    if request.user.is_authenticated:
        profile = request.user.profile

    context = {'profile': profile}
    return render(request, "main/home.html", context=context)
