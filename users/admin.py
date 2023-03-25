from django.contrib import admin
from .models import Department, Batch, CustomizedUser, Profile, AdminMessage


admin.site.register(CustomizedUser)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(Batch)
admin.site.register(AdminMessage)