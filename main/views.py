from django.shortcuts import render
from users.models import Student, Lecturer


def home(request):
    if request.user.is_authenticated:
        profile = request.user.profile

        # Generating this month data for the dashboard chart
        assignments = profile.this_month_assignments()
        meetings = profile.this_month_meetings()
        quizzes = profile.this_month_quizzes()

        context = {
            'profile': profile,
            'today_events': profile.today_events()[:8],
            'assignments': len(assignments),
            'quizzes': len(quizzes),
            'meetings': len(meetings),
        }
        return render(request, "main/home.html", context=context)

    context = {
        'students': Student.objects.all().count(),
        'lecturers': Lecturer.objects.all().count(),
    }
    return render(request, "main/home.html", context=context)


def today_events(request):
    """
    All today events page that get redirected after clicking
    'All Events' link in the dashboard page.
    """
    context = {
        'events': request.user.profile.today_events(),
    }
    return render(request, "main/template-parts/today-events.html", context=context)
