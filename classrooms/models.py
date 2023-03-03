from django.db import models
from django.contrib.auth.models import User


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(max_length=300)


