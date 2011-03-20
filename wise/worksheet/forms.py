from worksheet.models import Workspace
from django.forms import ModelForm, Textarea

class WorksheetForm(ModelForm):

    class Meta:
        model = Workspace
        exclude = ('owner')
        #widgets = {
            #'name': Textarea(),
        #}

    def save(self, owner=None, commit=True, *args, **kwargs):
        obj = super(WorksheetForm,self).save(commit=False,*args, **kwargs)
        obj.owner = owner
        if commit:
            obj.save()
        return obj
