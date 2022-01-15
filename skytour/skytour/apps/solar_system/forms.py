import datetime
from django import forms

"""
Still might want this for the Tracker view
"""
class DateRangeForm(forms.Form):
    start_date = forms.DateField(initial=datetime.datetime.now)
    end_date = forms.DateField()