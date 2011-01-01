from django import forms
from worksheet.models import Workspace

class WorksheetForm(forms.ModelForm, forms.BaseForm):
    class Meta:
        model = Workspace
        fields = ['name','public']
