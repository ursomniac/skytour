from django.urls import path
from .views import (
    WebsiteListView, GlossaryListView
)

urlpatterns = (
    path('website', WebsiteListView.as_view(), name='external-website-list'),
    path('glossary', GlossaryListView.as_view(), name='glossary-list'),
)