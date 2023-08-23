from django.urls import path
from .views import LibraryImageView, LibraryCatalogView

urlpatterns = (
    path('', LibraryImageView.as_view(), name='library-image-list'),
    path('catalog', LibraryCatalogView.as_view(), name='library-by-catalog'),
    path('<str:object_type>', LibraryImageView.as_view(), name='library-by-type'),
)