import datetime
from .models import Calendar

def get_upcoming_calendar(now, range=[-2, 5]):
    r0 = (now + datetime.timedelta(days=range[0])).date()
    r1 = (now + datetime.timedelta(days=range[1])).date()
    events = Calendar.objects.filter(date__range=[r0, r1]).order_by('date')
    return events