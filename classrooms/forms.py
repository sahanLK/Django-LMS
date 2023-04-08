from django import forms
from .models import Assignment, Submission, Classroom, Quiz, Meeting


class ClassroomCreateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), max_length=150, required=False)

    class Meta:
        model = Classroom
        fields = ['department', 'name', 'description']


class ClassroomUpdateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), max_length=150, required=False)

    class Meta:
        model = Classroom
        fields = ['name', 'lecturers', 'description']


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
        widget=forms.ClearableFileInput(
            attrs={'class': 'custom-file-input no-mw no-inside-name', 'id': 'assignment-submit'}),
        label='',
        required=False,
    )

    class Meta:
        model = Submission
        fields = ['file']


class AssignmentGradeForm(forms.ModelForm):
    """
    Assignment is graded by the lecturer after the submission.
    """
    grade = forms.CharField(max_length=20, required=False)
    lec_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional'}),
        required=False,
        max_length=150,
    )

    class Meta:
        model = Submission
        fields = ['grade', 'lec_comment']


"""
==============================
    QUIZ FORMS
==============================
"""


class MeetingCreationForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    meeting_url = forms.URLField(required=False, widget=forms.URLInput())
    start = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    recording_url = forms.URLField(required=False, widget=forms.URLInput())

    class Meta:
        model = Meeting
        fields = [
            'classroom',
            'topic',
            'start',
            'description',
            'meeting_url',
            'meeting_id',
            'meeting_pwd',
            'recording_url',
        ]


class MeetingUpdateForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    meeting_url = forms.URLField(required=False, widget=forms.URLInput())
    start = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    recording_url = forms.URLField(required=False, widget=forms.URLInput())

    class Meta:
        model = Meeting
        fields = [
            'topic',
            'start',
            'description',
            'meeting_url',
            'meeting_id',
            'meeting_pwd',
            'recording_url',
        ]

"""
==============================
    QUIZ FORMS
==============================
"""


class QuizCreateForm(forms.ModelForm):
    duration = forms.CharField(widget=forms.NumberInput(attrs={'min': 1, 'max': 300}))
    start = forms.DateTimeField(label="Start Time", widget=forms.TextInput(
        attrs={'type': 'date'},
    ))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Quiz
        fields = ['title', 'description',
                  'start', 'duration',
                  'accept_after_expired']
