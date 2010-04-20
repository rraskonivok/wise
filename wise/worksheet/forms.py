from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
