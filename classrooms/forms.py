from django import forms
from .models import Classroom


class ClassCreationForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['title', 'description']
