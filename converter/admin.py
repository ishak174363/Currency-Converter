from django.contrib import admin
from .models import Currency, ExchangeRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate', 'last_updated')
    list_filter = ('base_currency', 'last_updated')
    search_fields = ('base_currency__code', 'target_currency__code')
    ordering = ('-last_updated',)
    readonly_fields = ('last_updated',)
