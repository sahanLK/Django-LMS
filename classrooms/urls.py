from django.urls import path
from . import views
from . import fetchviews


urlpatterns = [
    path('classrooms/',
         views.ClassroomListView.as_view(), name='classrooms'),
    path('classroom/create-new/',
         views.ClassroomCreateView.as_view(), name='class-create'),
    path('classroom/<str:pk>/',
         views.ClassroomDetailView.as_view(), name='class-details'),
    path('classroom/<str:pk>/edit/',
         views.ClassroomUpdateView.as_view(), name='class-update'),
    path('classroom/<str:pk>/delete/',
         views.ClassroomDeleteView.as_view(), name='class-delete'),
    path('classroom/<str:pk>/post/create-new/',
         views.PostCreateView.as_view(), name='post-new'),
    path('classroom/<str:class_pk>/post/<str:pk>/',
         views.PostDetailView.as_view(), name='post-details'),
    path('classroom/<str:class_pk>/post/<str:pk>/update/',
         views.PostUpdateView.as_view(), name='post-update'),
    path('classroom/<str:class_pk>/post/<str:pk>/delete/',
         views.PostDeleteView.as_view(), name='post-delete'),
    path('classroom/<str:class_pk>/assignment/create-new/',
         views.AssignmentCreateView.as_view(), name='assignment-new'),
    path('classroom/<str:class_name>/assignment/<str:pk>/',
         views.assignment_detail_view, name='assignment-details'),
    path('classroom/<str:class_name>/assignment/<str:pk>/update/',
         views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('classroom/<str:class_name>/assignment/<str:pk>/delete/',
         views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('classroom/<str:class_name>/assignment/<str:pk>/unsubmit/'
         '', views.assignment_unsubmit_view, name='assignment-unsubmit'),
    path('classroom/<str:class_name>/assignment/<str:assignment_pk>/submission-details/',
         views.assignment_submissions_view, name='submit-details'),
    path('complete-review/<str:assignment_pk>/',
         views.assignment_complete_review_view, name='complete-review'),
    path('undo-complete-review/<str:assignment_pk>/',
         views.assignment_undo_complete_review_view, name='undo-review-complete'),
    path('assignments/all/<str:type>/',
         views.AssignmentListView.as_view(), name='assignments-list'),

    # Quizzes Urls
    path('quizzes/<str:type>/',
         views.QuizListView.as_view(), name='quiz-list'),
    path('classroom/<str:pk>/quiz/create-new/',
         views.QuizCreateView.as_view(), name='quiz-create'),
    path('classroom/<str:class_name>/quiz/<str:pk>/details/',
         views.QuizDetailView.as_view(), name='quiz-details'),
    path('classroom/<str:class_name>/quiz/<str:pk>/delete/',
         views.QuizDeleteView.as_view(), name='quiz-delete'),
    path('classroom/<str:class_name>/quiz/<str:pk>/edit/',
         views.QuizUpdateView.as_view(), name='quiz-update'),

    # Quiz question url
    path('classroom/<str:class_name>/quiz/<str:quiz_pk>/questions/',
         views.quiz_questions_and_answers_view, name='quiz-questions'),
    path('classroom/<str:class_name>/quiz/<str:quiz_pk>/live',
         views.quiz_live_view, name='quiz-live'),

    # Quiz response details page made by a student
    path('classroom/<str:class_name>/quiz/<str:quiz_pk>/response',
         views.quiz_stu_response_view, name='quiz-response'),

    # Quiz results page (for lecturer)
    path('classroom/<str:class_name>/quiz/<str:quiz_pk>/results',
         views.QuizResultsView.as_view(), name='quiz-results'),

    # Other fetch views
    path('classroom/<str:class_name>/quiz/<str:quiz_pk>/countdown',
         fetchviews.quiz_start_time_view, name='quiz-countdown'),


    # Meeting Urls
    path('meetings/<str:type>/',
         views.MeetingListView.as_view(), name='meetings-list'),
    path('classroom/<str:pk>/meeting/create-new/',
         views.MeetingCreateView.as_view(), name='meeting-create'),
    path('classroom/<str:class_name>/meeting/<str:pk>/details/',
         views.MeetingDetailView.as_view(), name='meeting-details'),
    path('classroom/<str:class_name>/meeting/<str:pk>/delete/',
         views.MeetingDeleteView.as_view(), name='meeting-delete'),
    path('classroom/<str:class_name>/meeting/<str:pk>/edit/',
         views.MeetingUpdateView.as_view(), name='meeting-update'),
]
