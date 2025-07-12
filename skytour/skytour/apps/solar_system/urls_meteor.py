from django.urls import path
from .views import (
    MeteorShowerWikiPopup, MeteorShowerListView, MeteorShowerDetailView
)

urlpatterns = (
    path('', MeteorShowerListView.as_view(), name='meteor-list'),
    path('<int:pk>', MeteorShowerDetailView.as_view(), name='meteor-detail'),
    path('wiki/<int:pk>', MeteorShowerWikiPopup.as_view(), name='meteor-wiki-popup'),
)