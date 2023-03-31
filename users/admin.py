from django.contrib import admin
from .models import CustomizedUser, Student, Lecturer


admin.site.register(CustomizedUser)
admin.site.register(Student)
admin.site.register(Lecturer)
# admin.site.register(AdminMessage)