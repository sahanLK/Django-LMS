from django.db import models
from django.contrib.auth.models import User


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, primary_key=True)
    subtitle_1 = models.CharField(max_length=200, null=True)
    subtitle_2 = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=300)
    # header_img = models.ImageField(upload_to="class_headers", null=True)

    def __str__(self):
        return f"{self.owner.username} | {self.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('classrooms')

# class Post(models.Model):
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
#     title = models.CharField(max_length=700)
#     body = models.TextField()
#

