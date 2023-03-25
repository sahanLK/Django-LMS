from django.db import models
from django.urls import reverse
from users.models import Profile, CustomizedUser, Batch, Department


class Classroom(models.Model):
    owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, unique=True)
    subtitle = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.owner.username} | {self.name}"

    @staticmethod
    def get_absolute_url():
        return reverse('classrooms')


class Post(models.Model):
    owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()
    date_modified = models.DateTimeField()
    title = models.CharField(max_length=300, unique=True)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"


class Assignment(models.Model):
    owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()
    date_modified = models.DateTimeField()
    date_due = models.DateTimeField()
    title = models.CharField(max_length=300, unique=True)
    content = models.TextField()
    documents = models.FileField(upload_to="assignments", null=True)

    def __str__(self):
        return f"{self.title} --> {self.classroom.name}"

    def get_absolute_url(self):
        return reverse('assignment-detail', kwargs={'class_pk': self.classroom.pk, 'pk': self.pk})


class SubmittedAssignment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    marked_done = models.BooleanField(default=False)
    grade = models.CharField(max_length=10, null=True)  # By lecturer
    comment = models.CharField(max_length=150, null=True)  # By lecturer
    file = models.FileField(upload_to="submitted_assignments", null=True)
    date_submitted = models.DateTimeField(null=True)

    def __str__(self):
        return f"Submission By: {self.profile.user.username}" \
               f" [ Ass.Name: {self.assignment.title}," \
               f" Class: {self.assignment.classroom.name} ]"
