from django.urls import path
from .views import (
    WebsiteListView, GlossaryListView, WebsiteEditView, WebsiteDeleteView, WebsiteDeleteResultView
)

urlpatterns = (
    path('website', WebsiteListView.as_view(), name='external-website-list'),
    path('website/edit/<int:pk>', WebsiteEditView.as_view(), name='website-edit-popup'),
    path('website/removed/result', WebsiteDeleteResultView.as_view(), name='website-delete-result'),
    path('website/delete/<int:pk>', WebsiteDeleteView.as_view(), name='website-delete-popup'),
    path('glossary', GlossaryListView.as_view(), name='glossary-list'),
)