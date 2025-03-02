from django import forms 
from .models import Website

class WebsiteAddForm(forms.ModelForm):
    name = forms.CharField()
    url = forms.URLField()

    class Meta:
        model = Website
        fields = ['name', 'url']

class WebsiteEditForm(forms.ModelForm):
    name = forms.CharField()
    url = forms.URLField()

    class Meta:
        model = Website
        fields = ['name', 'url']

class WebsiteDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)
    
    class Meta:
        model = Website
        fields = ['name', 'url', 'delete_confirm']
