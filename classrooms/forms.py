from django import forms
from .models import Assignment, SubmittedAssignment


class AssignmentCreationForm(forms.ModelForm):
    date_due = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    documents = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
        required=False,
    )

    class Meta:
        model = Assignment
        fields = ['title', 'content', 'date_due', 'documents']


class AssignmentSubmitForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input no-mw no-inside-name', 'id': 'assignment-submit'}),
        label='',
        required=False,
    )

    class Meta:
        model = SubmittedAssignment
        fields = ['file']


class AssignmentGradeForm(forms.ModelForm):
    """
    Assignment is graded by the lecturer after the submission.
    """
    grade = forms.CharField(max_length=20, required=False)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional'}),
        required=False,
        max_length=150,
    )

    class Meta:
        model = SubmittedAssignment
        fields = ['grade', 'comment']

