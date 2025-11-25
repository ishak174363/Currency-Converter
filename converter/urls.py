from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('rates/', views.GlobalRatesPageView.as_view(), name='global_rates_page'),
    path('info/real-time-rates/', views.InfoRealTimeRatesView.as_view(), name='info_real_time_rates'),
    path('info/currencies/', views.InfoCurrenciesView.as_view(), name='info_currencies'),
    path('info/secure-free/', views.InfoSecureFreeView.as_view(), name='info_secure_free'),
    path('currencies/', views.CurrenciesView.as_view(), name='get_currencies'),
    path('conversions/', views.ConversionView.as_view(), name='convert_currency'),
    path('rates/refresh/', views.RatesRefreshView.as_view(), name='update_rates'),
    path('rates/global/', views.GlobalRatesView.as_view(), name='global_rates'),
]
