from django import forms
from privatebeta.models import InviteRequest

class InviteRequestForm(forms.ModelForm, forms.BaseForm):
    class Meta:
        model = InviteRequest
        fields = ['email','info']
