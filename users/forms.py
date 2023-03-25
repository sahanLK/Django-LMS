from django.contrib.auth.forms import UserCreationForm, User
from .models import Profile, CustomizedUser, Batch, Department
from django import forms
from django.db.utils import OperationalError


def get_batches():
    batches = []
    try:
        batches = [(batch.year, batch.year) for batch in Batch.objects.all()]
    except OperationalError:
        pass
    return batches


def get_depts():
    depts = []
    try:
        depts = [(dept.name, dept.name) for dept in Department.objects.all() if dept]
    except OperationalError:
        pass
    return depts


def get_roles():
    roles = [(role, role) for role in ('Student', 'Lecturer')]
    return roles


def get_genders():
    genders = [(gender, gender) for gender in ('Male', 'Female')]
    return genders


class UserRegisterForm(UserCreationForm):
    gender = forms.ChoiceField(choices=get_genders())
    gender.widget.attrs = {'class': 'mw-150'}

    batch = forms.ChoiceField(choices=get_batches(), required=False)
    batch.widget.attrs = {'id': 'reg_batch', 'class': 'mw-100'}

    department = forms.ChoiceField(choices=get_depts(), required=True)
    department.widget.attrs = {'class': 'mw-400'}

    role = forms.ChoiceField(choices=get_roles(), required=True)
    role.widget.attrs = {'id': 'reg_role', 'class': 'mw-150'}

    id_photo = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'idPhotoInput'}),
        required=True)

    email = forms.EmailField(widget=forms.EmailInput)

    class Meta:
        model = CustomizedUser
        fields = ['username', 'first_name', 'last_name', 'gender',
                  'email', 'password1', 'password2', 'department',
                  'role', 'batch', 'id_photo']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create User and Profile without database save")
        user = super(UserRegisterForm, self).save(commit=True)
        cleaned_data = self.cleaned_data

        batch = Batch.objects.filter(year=cleaned_data['batch']).first()
        dept = Department.objects.get(name=cleaned_data['department'])

        user_profile = Profile(
            user=user,
            gender=cleaned_data['gender'],
            batch=batch,
            department=dept,
            role=cleaned_data['role'],
            id_photo=cleaned_data['id_photo'],
        )
        user_profile.save()
        return user, user_profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomizedUser
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=get_genders())
    gender.widget.attrs.update({'class': 'mw-150'})

    reg_no = forms.CharField(max_length=13)
    id_photo = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'idPhotoInput'}))
    profile_photo = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'id': 'profilePhotoInput'}))

    class Meta:
        model = Profile
        fields = ['reg_no', 'gender', 'id_photo', 'profile_photo']
