from django import forms 
from .models import Website, PDFManual

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
        fields = ['delete_confirm']

class PDFManualAbstractForm(forms.ModelForm):
    title = forms.CharField()
    pdf_file = forms.FileField()

    class Meta:
        abstract = True
        model = PDFManual
        fields = ['title', 'pdf_file']

class PDFManualAddForm(PDFManualAbstractForm):
    pass

class PDFManualEditForm(PDFManualAbstractForm):
    pass

class PDFManualDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']