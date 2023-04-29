from django.contrib import admin
from .models import (
    Classroom,
    Assignment,
    Post,
    Submission,
    SubmissionFile,
    Quiz,
    Meeting,
    QuizQuestion,
    QuizQuestionAnswer,
    QuizStudentResponse,
    QuizStudentResponseQuestion,
    QuizStudentResponseQuestionAnswer,
)

admin.site.register(Classroom)
admin.site.register(Post)
admin.site.register(Meeting)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(SubmissionFile)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizQuestionAnswer)
admin.site.register(QuizStudentResponse)
admin.site.register(QuizStudentResponseQuestion)
admin.site.register(QuizStudentResponseQuestionAnswer)


