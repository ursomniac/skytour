from django import forms 
from django.forms import inlineformset_factory
from .models import Website, PDFManual, Calendar, CalendarEventReference
from .vocabs import REFERENCE_MODEL_CHOICES

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
    op = forms.CharField(widget = forms.HiddenInput(), initial='add')
    pass

class PDFManualEditForm(PDFManualAbstractForm):
    op = forms.CharField(widget = forms.HiddenInput(), initial='edit')
    pass

class PDFManualDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)
    op = forms.CharField(widget = forms.HiddenInput(), initial='delete')

    class Meta:
        fields = ['delete_confirm']

FORM_REFERENCE_MODEL_CHOICES = [('', '---------------')] + REFERENCE_MODEL_CHOICES
class CalendarEventReferenceForm(forms.ModelForm):
    reference_type = forms.ChoiceField (
        choices = FORM_REFERENCE_MODEL_CHOICES,
    )
    reference = forms.CharField(
    )

    class Meta:
        model = CalendarEventReference
        fields = ['reference_type', 'reference']

CalendarAddEventReferenceFormset = inlineformset_factory(
    Calendar, 
    CalendarEventReference,
    form = CalendarEventReferenceForm,
    fields = ['reference_type', 'reference'],
    extra = 3,
    can_delete = True
)

CalendarEditEventReferenceFormset = inlineformset_factory(
    Calendar, 
    CalendarEventReference,
    form = CalendarEventReferenceForm,
    fields = ['reference_type', 'reference'],
    extra = 0,
    can_delete = True
)

class CalendarEntryForm(forms.Form):
    class Meta:
        model = Calendar
        fields = ['date', 'time', 'title', 'description', 'event_type',]

