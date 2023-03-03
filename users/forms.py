from django.contrib.auth.forms import UserCreationForm, User
from .models import Profile
from django import forms


DEPT_CHOICES = [
    ("TCT", "TCT"),
    ("ECT", "ECT"),
    ("FDT", "FDT"),
    ("FDT", "FDT"),
    ("MLM", "MLM"),
    ("TTM", "TTM"),
]

ROLE_CHOICES = [
    ('Student', 'Student'),
    ('Lecturer', 'Lecturer'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]


class UserRegisterForm(UserCreationForm):
    reg_no = forms.CharField(max_length=13, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    academic_year = forms.CharField(widget=forms.NumberInput, max_length=4, required=True)
    department = forms.ChoiceField(choices=DEPT_CHOICES, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    id_photo = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username', 'reg_no', 'first_name', 'last_name', 'gender', 'email', 'password1', 'password2', 'academic_year',
                  'department', 'role', 'id_photo']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create User and Profile without database save")
        user = super(UserRegisterForm, self).save(commit=True)
        cleaned_data = self.cleaned_data
        user_profile = Profile(
            user=user,
            reg_no=cleaned_data['reg_no'],
            academic_year=cleaned_data['academic_year'],
            department=cleaned_data['department'],
            role=cleaned_data['role'],
            id_photo=cleaned_data['id_photo'],
        )
        user_profile.save()
        return user, user_profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    department = forms.ChoiceField(choices=DEPT_CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    class Meta:
        model = Profile
        fields = ['reg_no', 'gender', 'academic_year', 'department', 'id_photo']


