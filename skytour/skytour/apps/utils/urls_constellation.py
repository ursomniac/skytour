from django.urls import path
from .views import ConstellationDetailView, ConstellationListView, ConstellationWikiPopup

urlpatterns = (
    path('', ConstellationListView.as_view(), name='constellation-list'),
    path('wiki/<slug:slug>', ConstellationWikiPopup.as_view(), name='constellation-wiki'),
    path('<slug:slug>', ConstellationDetailView.as_view(), name='constellation-detail'),
)