from worksheet.models import Workspace
from django.forms import ModelForm, Textarea, BaseForm

class WorksheetForm(ModelForm):

    class Meta:
        model = Workspace
        fields = ['name','public']

        widgets = {
            'name': Textarea(),
            'public': Textarea(),
        }
