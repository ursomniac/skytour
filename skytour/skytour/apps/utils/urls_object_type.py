from django.urls import path
from .views import ObjectTypeListView, ObjectTypeDetailView

urlpatterns = (
    path('', ObjectTypeListView.as_view(), name='object-type-list'),
    path('<slug:slug>', ObjectTypeDetailView.as_view(), name='object-type-detail'),
)