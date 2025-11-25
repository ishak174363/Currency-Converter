from django.db import models
from django.utils import timezone


class Currency(models.Model):
    """Model to store currency information"""
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True)
    
    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ExchangeRate(models.Model):
    """Model to cache exchange rates"""
    base_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='base_rates'
    )
    target_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='target_rates'
    )
    rate = models.DecimalField(max_digits=20, decimal_places=6)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('base_currency', 'target_currency')
        ordering = ['base_currency', 'target_currency']
    
    def __str__(self):
        return f"{self.base_currency.code} -> {self.target_currency.code}: {self.rate}"
