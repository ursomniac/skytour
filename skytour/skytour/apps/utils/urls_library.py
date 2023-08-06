from django.urls import path
from .views import LibraryImageView

urlpatterns = (
    path('', LibraryImageView.as_view(), name='library-image-list'),
    path('<str:object_type>', LibraryImageView.as_view(), name='library-by-type'),
)