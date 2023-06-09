from django.urls import path, include
from .views import CountryListAPIView

app_name = 'countries'

urlpatterns = [
    path('countries/', CountryListAPIView.as_view(), name='country-list'),
]
