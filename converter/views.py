from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
from django.shortcuts import render
from .models import Currency
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
