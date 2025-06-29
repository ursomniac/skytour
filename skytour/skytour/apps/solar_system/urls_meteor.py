from django.urls import path
from .views import (
    MeteorShowerWikiPopup
)

urlpatterns = (
    path('wiki/<int:pk>', MeteorShowerWikiPopup.as_view(), name='asteroid-wiki-popup'),
)