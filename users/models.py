from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_no = models.CharField(max_length=13)
    gender = models.CharField(max_length=6, default='Male')
    academic_year = models.IntegerField()
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=8)
    id_photo = models.ImageField(default='default.jpg', upload_to="id_photos")

    def __str__(self):
        return f"{self.role} | {self.user.username}"
