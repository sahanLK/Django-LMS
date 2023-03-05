from django.db import models
from django.contrib.auth.models import User
import datetime


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    subtitle_1 = models.CharField(max_length=200, null=True)
    subtitle_2 = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=300)
    header_img = models.ImageField(upload_to="class_headers", null=True)

    def __str__(self):
        return f"{self.owner.username} | {self.name}"

    @staticmethod
    def get_absolute_url():
        from django.urls import reverse
        return reverse('classrooms')


class Post(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()
    date_modified = models.DateTimeField()
    title = models.CharField(max_length=300)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateField(default=datetime.datetime.now())
    date_modified = models.DateTimeField()
    date_due = models.DateTimeField(default=datetime.datetime.now())
    title = models.CharField(max_length=300)
    content = models.TextField()
    document = models.FileField(upload_to="assignments")

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"


class Notification(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateField(default=datetime.datetime.now())
    date_modified = models.DateTimeField()
    title = models.CharField(max_length=300)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"
