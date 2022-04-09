from django.urls import path
from .pdf import SSOPDFView

urlpatterns = (
    path('<str:object_type>/<str:object_id>', SSOPDFView.as_view(), name='sso-pdf'),
)