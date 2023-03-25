from django.db import models
from django.contrib.auth.models import AbstractUser, User


class Batch(models.Model):
    """
    Represents a one single batch in the UCR
    """
    year = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.year} Batch"


class Department(models.Model):
    """
    Represents a department in the UCR
    """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.name}"


class CustomizedUser(AbstractUser):
    """
    Customized User model
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username}{'( Administrator )' if self.is_superuser else ''}"


class Profile(models.Model):
    """
    User profiles. Both students and lecturers have a profile.
    """
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True)
    reg_no = models.CharField(max_length=13, null=True, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, default='Male')
    role = models.CharField(max_length=8)
    id_photo = models.ImageField(upload_to="id_photos")
    profile_photo = models.ImageField(upload_to="profile_photos", default="profile.png", null=True)

    def __str__(self):
        return f"{self.role} | {self.user.username}"

    @property
    def completed(self) -> int:
        """
        Return how many percent the user has completed setting up their profile
        :return:
        """
        completed = 100
        if not self.reg_no:
            completed -= 10
        if 'profile_photos' not in str(self.profile_photo.url).split('/'):
            completed -= 10
        return completed


class AdminMessage(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.name} -> {self.subject}"
