from worksheet.models import Workspace
from django.forms import ModelForm, Textarea

class WorksheetForm(ModelForm):

    class Meta:
        model = Workspace
        exclude = ('owner')
        widgets = {
            'name': Textarea(),
        }

    def save(self, owner, commit=True, *args, **kwargs):
        project = super(WorksheetForm,self).save(commit=False,*args, **kwargs)
        project.owner = owner
        if commit:
            project.save()
        return project
