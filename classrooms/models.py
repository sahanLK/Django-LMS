from django.contrib.auth.models import User
from django.db import models


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    subtitle_1 = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=100)
    header_img = models.ImageField(upload_to="class_headers", null=True)

    def __str__(self):
        return f"{self.owner.username} | {self.name}"

    @staticmethod
    def get_absolute_url():
        from django.urls import reverse
        return reverse('classrooms')


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()
    date_modified = models.DateTimeField()
    title = models.CharField(max_length=300)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"

    # def get_absolute_url(self):
    #     from django.urls import reverse
    #     return reverse('post-details', kwargs={'pk': self.pk})


class Assignment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()
    date_modified = models.DateTimeField()
    date_due = models.DateTimeField()
    title = models.CharField(max_length=300)
    content = models.TextField()
    submitted = models.BooleanField(default=False)
    grade = models.CharField(max_length=10, default='Not Graded')
    documents = models.FileField(upload_to="assignments")

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assignment-detail', kwargs={'class_pk': self.classroom.pk, 'pk': self.pk})


# class Notification(models.Model):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
#     date_posted = models.DateField()
#     date_modified = models.DateTimeField()
#     title = models.CharField(max_length=300)
#     content = models.TextField()
#
#     def __str__(self):
#         return f"{self.title} --> {self.classroom.name}"
