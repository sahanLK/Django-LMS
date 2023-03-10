from django import forms
from .models import Assignment


class AssignmentCreationForm(forms.ModelForm):
    date_due = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    documents = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Assignment
        fields = ['title', 'content', 'date_due', 'documents']


class AssignmentSubmitForm(forms.ModelForm):
    documents = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': 'custom-file-input', 'id': 'assignment-submit'}
        ),
        label='',
    )

    class Meta:
        model = Assignment
        fields = ['documents']

