from django.urls import path
from .views import LibraryImageView, LibraryCatalogView, LibraryConstellationView

urlpatterns = (
    path('', LibraryImageView.as_view(), name='library-image-list'),
    path('catalog', LibraryCatalogView.as_view(), name='library-by-catalog'),
    path('constellation', LibraryConstellationView.as_view(), name='library-by-constellation-default'),
    path('constellation/<str:abbr>', LibraryConstellationView.as_view(), name='library-by-constellation'),
    path('<str:object_type>', LibraryImageView.as_view(), name='library-by-type'),
)