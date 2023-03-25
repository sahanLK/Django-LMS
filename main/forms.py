from django import forms
from users.models import AdminMessage


class AdminMessageForm(forms.ModelForm):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Name', 'class': 'w3-input w3-border'}))
    email = forms.CharField(label='', widget=forms.EmailInput(attrs={
        'placeholder': 'Email', 'class': 'w3-input w3-border'}))
    subject = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Subject', 'class': 'w3-input w3-border'}))
    message = forms.CharField(label='', widget=forms.Textarea(attrs={
        'placeholder': 'Message', 'class': 'w3-input w3-border', 'rows': 4}))

    class Meta:
        model = AdminMessage
        fields = ('name', 'email', 'subject', 'message')
