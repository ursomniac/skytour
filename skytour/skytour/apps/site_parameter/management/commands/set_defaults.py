import datetime, pytz
from django.core.management.base import BaseCommand


def set_defaults():
    pass

class Command(BaseCommand):
    help = 'Set up site parameter defaults'
    
    def handle(self, *args, **kwargs):
        # Default Location pk
        # Default DSO Magnitude Limit
        # Default Hour Angle Span
        # Default Observing Session
        # Default Latitude
        # Default Longitude
        pass
