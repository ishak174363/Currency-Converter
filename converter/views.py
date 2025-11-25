from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
from django.shortcuts import render
from .models import Currency, ExchangeRate
from .serializers import (
    CurrencySerializer, 
    ConversionRequestSerializer, 
    ConversionResponseSerializer
)
from .services import CurrencyService


class IndexView(View):
    """Render the main currency converter page"""
    def get(self, request):
        return render(request, 'index.html')


class GlobalRatesPageView(View):
    """Render the global exchange rates page"""
    def get(self, request):
        return render(request, 'global_rates.html')


class InfoRealTimeRatesView(View):
    """Render the real-time rates info page"""
    def get(self, request):
        return render(request, 'info_real_time_rates.html')


class InfoCurrenciesView(View):
    """Render the currencies info page"""
    def get(self, request):
        return render(request, 'info_currencies.html')


class InfoSecureFreeView(View):
    """Render the secure & free info page"""
    def get(self, request):
        return render(request, 'info_secure_free.html')


class CurrenciesView(APIView):
    """Get list of all available currencies"""
    def get(self, request):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data)


class ConversionView(APIView):
    """Convert currency from one to another"""
    def post(self, request):
        serializer = ConversionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = CurrencyService.convert_currency(
                from_currency=serializer.validated_data['from_currency'],
                to_currency=serializer.validated_data['to_currency'],
                amount=serializer.validated_data['amount']
            )
            
            response_serializer = ConversionResponseSerializer(result)
            return Response(response_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred during conversion'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RatesRefreshView(APIView):
    """Manually trigger exchange rate update"""
    def post(self, request):
        base_currency = request.data.get('base_currency', 'USD')
        
        try:
            success = CurrencyService.update_exchange_rates(base_currency)
            
            if success:
                return Response({'message': 'Exchange rates updated successfully'})
            else:
                return Response(
                    {'error': 'Failed to update exchange rates'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GlobalRatesView(APIView):
    """Get global exchange rates compared to a base currency"""
    def get(self, request):
        # Get base currency from query parameter, default to BDT
        base_currency = request.query_params.get('base', 'BDT').upper()
        
        try:
            # Get or create base currency
            base_curr = Currency.objects.get(code=base_currency)
            
            # Get all exchange rates from the base currency
            rates = ExchangeRate.objects.filter(
                base_currency__code=base_currency
            ).select_related('target_currency').order_by('target_currency__code')
            
            # If no rates found, update them
            if not rates.exists():
                CurrencyService.update_exchange_rates(base_currency)
                rates = ExchangeRate.objects.filter(
                    base_currency__code=base_currency
                ).select_related('target_currency').order_by('target_currency__code')
            
            # Format data for table display
            rates_data = [
                {
                    'currency_code': rate.target_currency.code,
                    'currency_name': rate.target_currency.name,
                    'symbol': rate.target_currency.symbol,
                    'rate': float(rate.rate),
                    'last_updated': rate.last_updated
                }
                for rate in rates
            ]
            
            return Response({
                'base_currency': base_currency,
                'rates': rates_data,
                'total_currencies': len(rates_data)
            })
            
        except Currency.DoesNotExist:
            return Response(
                {'error': f'Currency {base_currency} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
