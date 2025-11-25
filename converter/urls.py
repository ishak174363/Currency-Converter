from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('currencies/', views.CurrenciesView.as_view(), name='get_currencies'),
    path('conversions/', views.ConversionView.as_view(), name='convert_currency'),
    path('rates/refresh/', views.RatesRefreshView.as_view(), name='update_rates'),
]
