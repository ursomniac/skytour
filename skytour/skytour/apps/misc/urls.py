from django.urls import path
from .views import (
    WebsiteListView, 
    GlossaryListView,
    WebsiteEditView, 
    WebsiteDeleteView, 
    WebsiteDeleteResultView,
    WebsiteEditResultView,
    PDFManualListView,
    PDFManualEditView,
    PDFManualEditResultView,
    PDFManualDeleteView,
    PDFManualDeleteResultView,
)

urlpatterns = (
    path('website', WebsiteListView.as_view(), name='external-website-list'),
    path('website/edit/<int:pk>', WebsiteEditView.as_view(), name='website-edit-popup'),
    path('website/edit/result', WebsiteEditResultView.as_view(), name='website-edit-result'),
    path('website/removed/result', WebsiteDeleteResultView.as_view(), name='website-delete-result'),
    path('website/delete/<int:pk>', WebsiteDeleteView.as_view(), name='website-delete-popup'),
    path('glossary', GlossaryListView.as_view(), name='glossary-list'),
    path('manual', PDFManualListView.as_view(), name='manual-list'),
    path('manual/edit/<int:pk>', PDFManualEditView.as_view(), name='manual-edit'),
    path('manual/edit/result', PDFManualEditResultView.as_view(), name='manual-edit-result'),
    path('manual/delete/<int:pk>', PDFManualDeleteView.as_view(), name='manual-delete'),
    path('manual/delete/result', PDFManualDeleteResultView.as_view(), name='manual-delete-result')
)