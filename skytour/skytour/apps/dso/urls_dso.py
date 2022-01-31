from django.urls import path
from .views import DSODetailView, DSOListView

urlpatterns = (
    path('', DSOListView.as_view(), name='dso-list'),
    path('<int:pk>', DSODetailView.as_view(), name='dso-detail'),
)