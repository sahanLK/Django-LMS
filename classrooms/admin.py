from django.contrib import admin
from .models import Classroom, Notification, Assignment, Post

admin.site.register(Classroom)
admin.site.register(Notification)
admin.site.register(Assignment)
admin.site.register(Post)
