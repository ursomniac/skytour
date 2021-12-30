from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from .models import BrightStar

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    