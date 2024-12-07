from django import forms

class ChatForm(forms.Form):
    user_message = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={"placeholder": "Enter your message", "class": "form-control"})
    )
