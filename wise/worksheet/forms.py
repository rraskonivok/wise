from django import forms

class WorksheetForm(forms.Form):
    name = forms.CharField(max_length=200,
            widget=forms.TextInput(attrs={'class':'text_field'}))
    public = forms.BooleanField( required=False )
