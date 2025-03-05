from django import forms
from .models import (
    SiteParameterPositiveInteger,
    SiteParameterLink,
    SiteParameterFloat,
    SiteParameterImage,
    SiteParameterNumber,
    SiteParameterPDFFile,
    SiteParameterString,
)

class SiteParameterPositiveIntegerForm(forms.ModelForm):
    value = forms.IntegerField(min_value=0)

    class Meta:
        model = SiteParameterPositiveInteger
        fields = ['value',]

class SiteParameterFloatForm(forms.ModelForm):
    value = forms.FloatField()

    class Meta:
        model = SiteParameterFloat
        fields = ['value',]

class SiteParameterStringForm(forms.ModelForm):
    value = forms.CharField()

    class Meta:
        model = SiteParameterString
        fields = ['value',]


###########################

class SiteParameterNumberForm(forms.ModelForm):
    value = forms.IntegerField()

    class Meta:
        model = SiteParameterNumber
        fields = ['value',]

###########################

class SiteParameterImageForm(forms.ModelForm):
    value = forms.ImageField()

    class Meta:
        model = SiteParameterImage
        fields = ['value',]

class SiteParameterLinkForm(forms.ModelForm):
    value = forms.URLField()

    class Meta:
        model = SiteParameterLink
        fields = ['value',]

class SiteParameterPDFForm(forms.ModelForm):
    value = forms.FileField()

    class Meta:
        model = SiteParameterPDFFile
        fields = ['value',]