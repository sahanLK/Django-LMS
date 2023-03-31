from django.db import models
from django.contrib.auth.models import AbstractUser
from main.models import Batch, Department
from typing import Union


class CustomizedUser(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    gender = models.CharField(max_length=6)

    def __str__(self):
        username = "Administrator" if self.is_superuser else self.username
        return f"{username} [ {self.email} ]"

    @property
    def role(self):
        if self.is_superuser:
            return 'superuser'
        elif len(Student.objects.filter(user=self)) != 0:
            return 'student'
        elif len(Lecturer.objects.filter(user=self)) != 0:
            return 'lecturer'

    @property
    def profile(self):
        """
        Return the related profile for the user.
        Profile can only be <Student> or <Lecturer> instance.
        :return:
        """
        profile = None
        if self.role == 'student':
            profile = Student.objects.get(user=self)
        elif self.role == 'lecturer':
            profile = Lecturer.objects.get(user=self)
        else:
            # This should never happen
            print("Undetected Role")
        return profile


class Student(models.Model):
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE, related_name='student')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, upload_to="stu_profile_pics")
    id_pic = models.ImageField(null=True, upload_to="stu_id_pics")

    def __str__(self):
        return f"Student: {self.user.username} [{self.department.name}]"


class Lecturer(models.Model):
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE, related_name='lecturer')
    departments = models.ManyToManyField(Department, blank=True)
    profile_pic = models.ImageField(null=True, upload_to="lec_profile_pics")

    def __str__(self):
        return f"Lecturer: {self.user.username}"


class AdminMessage(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.name} -> {self.subject}"
