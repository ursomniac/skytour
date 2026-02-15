from django.urls import path
from .views import (
    CalcModulusView,
    CalcSQSToSQMView,
    CalcSQMToBortleView,
    CalcExposureFromFramesView,
    CalcFramesFromExposureView,
    CalcAngularSizeView,
    CalcJDToDateView,
    CalcDateToJDView,
    CalcRedshiftToDistanceView
)

urlpatterns = (
    path('calc/modulus', CalcModulusView.as_view(), name='calc-modulus'),
    path('calc/sqs2sqm', CalcSQSToSQMView.as_view(), name='calc-sqm'),
    path('calc/sqm2bortle', CalcSQMToBortleView.as_view(), name='calc-bortle'),
    path('calc/framesexposure', CalcExposureFromFramesView.as_view(), name='calc-exposure-time'),
    path('calc/exposureframes', CalcFramesFromExposureView.as_view(), name='calc-frames'),
    path('calc/angsize', CalcAngularSizeView.as_view(), name='calc-angsize'),
    path('calc/jd2date', CalcJDToDateView.as_view(), name='calc-jd2date'),
    path('calc/date2jd', CalcDateToJDView.as_view(), name='calc-date2jd'),
    path('calc/redshift', CalcRedshiftToDistanceView.as_view(), name = 'calc-redshift'),
)