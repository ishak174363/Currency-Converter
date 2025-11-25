from rest_framework import serializers
from .models import Currency, ExchangeRate


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model"""
    
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeRate model"""
    
    class Meta:
        model = ExchangeRate
        fields = ['base_currency', 'target_currency', 'rate', 'last_updated']


class ConversionRequestSerializer(serializers.Serializer):
    """Serializer for currency conversion requests"""
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)


class ConversionResponseSerializer(serializers.Serializer):
    """Serializer for currency conversion responses"""
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    exchange_rate = serializers.DecimalField(max_digits=20, decimal_places=6)
    last_updated = serializers.DateTimeField()
