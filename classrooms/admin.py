from django.contrib import admin
from .models import Classroom, Assignment, Post, SubmittedAssignment

admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(Post)
admin.site.register(SubmittedAssignment)
