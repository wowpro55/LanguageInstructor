from django import forms

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=255)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
