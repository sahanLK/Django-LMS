import os.path
from datetime import datetime
from django.db import models
from django.urls import reverse
from users.models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from main.funcs import d_t


class Classroom(models.Model):
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='owner')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    lecturers = models.ManyToManyField(Lecturer)
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=150, null=True,  blank=True)
    background_img = models.ImageField(null=True, blank=True)

    class Meta:
        unique_together = (('department', 'name'),)

    def __str__(self):
        return f"Class: {self.name} [{self.department}]"


class Post(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    date_pub = models.DateTimeField()
    date_last_mod = models.DateTimeField()
    content = models.TextField()

    class Meta:
        unique_together = (('classroom', 'title'),)

    def __str__(self):
        return f"Post: {self.title} [{self.classroom}]"


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    date_pub = models.DateTimeField()
    date_last_mod = models.DateTimeField()
    date_due = models.DateTimeField()
    content = models.TextField()
    file = models.FileField(null=True, blank=True)
    review_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment: {self.title} [ {self.classroom} ]"

    @property
    def has_due_expired(self):
        if d_t(self.date_due) < d_t(datetime.now()):
            return True
        return False

    @property
    def pending_submissions(self) -> int:
        _all_stu = self.classroom.department.student_set.count()
        _all_sub_done = self.submission_set.count()
        pending = int(_all_stu) - int(_all_sub_done)
        return pending


class Meeting(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    topic = models.CharField(max_length=300)
    time_start = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Meeting: {self.topic} [Class-> {self.classroom.name}" \
               f" {self.classroom.department.batch.year} Batch]"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    owner = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_sub = models.DateTimeField()
    grade = models.CharField(max_length=20, null=True, blank=True)
    file = models.FileField(upload_to="submitted_assignments", blank=True, null=True)
    lec_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Submission By: {self.owner.user.username} [Assignment-> {self.assignment.title}]"

    @property
    def is_late_submit(self):
        """
        If the submission is a late submit or not.
        :return:
        """
        if d_t(self.date_sub) > d_t(self.assignment.date_due):
            return True
        return False

    def get_short_file_name(self):
        name = self.file.name
        return os.path.basename(name)[-28:]



















#
#
# class Classroom(models.Model):
#     owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
#     name = models.CharField(max_length=300, unique=True)
#     subtitle = models.CharField(max_length=200, null=True)
#
#     def __str__(self):
#         return f"{self.owner.username} | {self.name}"
#
#     @staticmethod
#     def get_absolute_url():
#         return reverse('classrooms')
#
#
# class Post(models.Model):
#     owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
#     date_posted = models.DateTimeField()
#     date_modified = models.DateTimeField()
#     title = models.CharField(max_length=300, unique=True)
#     content = models.TextField()
#
#     def __str__(self):
#         return f"{self.title} --> {self.classroom.name}"
#
#
# class Assignment(models.Model):
#     owner = models.ForeignKey(CustomizedUser, on_delete=models.CASCADE)
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
#     date_posted = models.DateTimeField()
#     date_modified = models.DateTimeField()
#     date_due = models.DateTimeField()
#     title = models.CharField(max_length=300, unique=True)
#     content = models.TextField()
#     documents = models.FileField(upload_to="assignments", null=True)
#
#     def __str__(self):
#         return f"{self.title} --> {self.classroom.name}"
#
#     def get_absolute_url(self):
#         return reverse('assignment-detail', kwargs={'class_pk': self.classroom.pk, 'pk': self.pk})
#
#
# class SubmittedAssignment(models.Model):
#     assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
#     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     marked_done = models.BooleanField(default=False)
#     grade = models.CharField(max_length=10, null=True)  # By lecturer
#     comment = models.CharField(max_length=150, null=True)  # By lecturer
#     file = models.FileField(upload_to="submitted_assignments", null=True)
#     date_submitted = models.DateTimeField(null=True)
#
#     def __str__(self):
#         return f"Submission By: {self.profile.user.username}" \
#                f" [ Ass.Name: {self.assignment.title}," \
#                f" Class: {self.assignment.classroom.name} ]"
