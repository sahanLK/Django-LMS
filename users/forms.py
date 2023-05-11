from django.contrib.auth.forms import UserCreationForm
from .models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from django import forms
from django.db.utils import ProgrammingError


GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]


def get_batches():
    try:
        return [(batch, batch) for batch in Batch.objects.all()]
    except ProgrammingError:
        return []


class UserRegisterForm(UserCreationForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    gender.widget.attrs = {'class': 'mw-150'}

    class Meta:
        model = CustomizedUser
        fields = ['username', 'first_name', 'last_name',
                  'email', 'gender', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    gender = forms.ChoiceField(disabled=True, choices=GENDER_CHOICES)
    gender.widget.attrs = {'class': 'mw-150'}

    class Meta:
        model = CustomizedUser
        fields = ['username', 'email', 'first_name', 'last_name', 'gender']


class StudentCreationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['department']

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].widget.attrs.update({'id': 'deptSelect'})


class StudentUpdateForm(forms.ModelForm):
    profile_pic = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'profilePhotoInput'}),
        required=False,
        label="Profile Photo")

    id_pic = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'idPhotoInput'}),
        required=False,
        label="ID Photo")

    class Meta:
        model = Student
        fields = ['id_pic', 'profile_pic']


class LecturerCreationForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = []


class LecturerUpdateForm(forms.ModelForm):
    profile_pic = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'idPhotoInput'}),
        required=False,
        label="Profile Photo")

    class Meta:
        model = Lecturer
        fields = ['profile_pic']


class LecturerDepartmentEnrollForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['departments']
