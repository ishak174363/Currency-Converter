import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Currency, ExchangeRate


class CurrencyService:
    """Service class for currency conversion operations"""
    
    @staticmethod
    def get_or_create_currency(code, name='', symbol=''):
        """Get or create a currency"""
        currency, created = Currency.objects.get_or_create(
            code=code.upper(),
            defaults={'name': name, 'symbol': symbol}
        )
        return currency
    
    @staticmethod
    def fetch_exchange_rates(base_currency='USD'):
        """Fetch exchange rates from external API"""
        try:
            url = f"{settings.EXCHANGE_RATE_API_URL}{base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data:
                return data['rates']
            return None
        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            return None
    
    @staticmethod
    def update_exchange_rates(base_currency='USD'):
        """Update exchange rates in database"""
        rates = CurrencyService.fetch_exchange_rates(base_currency)
        
        if not rates:
            return False
        
        base_curr = CurrencyService.get_or_create_currency(base_currency)
        
        for currency_code, rate in rates.items():
            target_curr = CurrencyService.get_or_create_currency(currency_code)
            
            ExchangeRate.objects.update_or_create(
                base_currency=base_curr,
                target_currency=target_curr,
                defaults={'rate': Decimal(str(rate))}
            )
        
        return True
    
    @staticmethod
    def get_exchange_rate(from_currency, to_currency):
        """Get exchange rate between two currencies"""
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        # If same currency, rate is 1
        if from_curr == to_curr:
            return Decimal('1.0'), timezone.now()
        
        try:
            # Try to get from database
            exchange_rate = ExchangeRate.objects.get(
                base_currency__code=from_curr,
                target_currency__code=to_curr
            )
            
            # Check if rate is older than 24 hours
            if timezone.now() - exchange_rate.last_updated > timedelta(hours=24):
                # Update rates
                CurrencyService.update_exchange_rates(from_curr)
                exchange_rate.refresh_from_db()
            
            return exchange_rate.rate, exchange_rate.last_updated
            
        except ExchangeRate.DoesNotExist:
            # Fetch new rates
            CurrencyService.update_exchange_rates(from_curr)
            
            try:
                exchange_rate = ExchangeRate.objects.get(
                    base_currency__code=from_curr,
                    target_currency__code=to_curr
                )
                return exchange_rate.rate, exchange_rate.last_updated
            except ExchangeRate.DoesNotExist:
                raise ValueError(f"Exchange rate not available for {from_curr} to {to_curr}")
    
    @staticmethod
    def convert_currency(from_currency, to_currency, amount):
        """Convert amount from one currency to another"""
        rate, last_updated = CurrencyService.get_exchange_rate(from_currency, to_currency)
        converted_amount = Decimal(str(amount)) * rate
        
        return {
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'amount': Decimal(str(amount)),
            'converted_amount': converted_amount,
            'exchange_rate': rate,
            'last_updated': last_updated
        }
    
    @staticmethod
    def initialize_currencies():
        """Initialize ALL world currencies by fetching from API"""
        print("Fetching all available currencies from API...")
        
        # Fetch rates from USD to get all available currencies
        rates = CurrencyService.fetch_exchange_rates('USD')
        
        if not rates:
            print("Failed to fetch currencies from API. Using fallback list.")
            # Fallback to basic currencies if API fails
            fallback_currencies = [
                ('USD', 'US Dollar', '$'),
                ('EUR', 'Euro', '€'),
                ('GBP', 'British Pound', '£'),
                ('JPY', 'Japanese Yen', '¥'),
                ('AUD', 'Australian Dollar', 'A$'),
                ('CAD', 'Canadian Dollar', 'C$'),
                ('CHF', 'Swiss Franc', 'CHF'),
                ('CNY', 'Chinese Yuan', '¥'),
                ('INR', 'Indian Rupee', '₹'),
            ]
            for code, name, symbol in fallback_currencies:
                CurrencyService.get_or_create_currency(code, name, symbol)
            return
        
        # Currency names and symbols mapping (for better display)
        currency_info = {
            'USD': ('US Dollar', '$'), 'EUR': ('Euro', '€'), 'GBP': ('British Pound', '£'),
            'JPY': ('Japanese Yen', '¥'), 'CHF': ('Swiss Franc', 'CHF'), 'CAD': ('Canadian Dollar', 'C$'),
            'AUD': ('Australian Dollar', 'A$'), 'NZD': ('New Zealand Dollar', 'NZ$'),
            'CNY': ('Chinese Yuan', '¥'), 'INR': ('Indian Rupee', '₹'), 'KRW': ('South Korean Won', '₩'),
            'SGD': ('Singapore Dollar', 'S$'), 'HKD': ('Hong Kong Dollar', 'HK$'),
            'MXN': ('Mexican Peso', '$'), 'BRL': ('Brazilian Real', 'R$'), 'ZAR': ('South African Rand', 'R'),
            'RUB': ('Russian Ruble', '₽'), 'TRY': ('Turkish Lira', '₺'), 'SEK': ('Swedish Krona', 'kr'),
            'NOK': ('Norwegian Krone', 'kr'), 'DKK': ('Danish Krone', 'kr'), 'PLN': ('Polish Złoty', 'zł'),
            'THB': ('Thai Baht', '฿'), 'IDR': ('Indonesian Rupiah', 'Rp'), 'MYR': ('Malaysian Ringgit', 'RM'),
            'PHP': ('Philippine Peso', '₱'), 'CZK': ('Czech Koruna', 'Kč'), 'ILS': ('Israeli New Shekel', '₪'),
            'CLP': ('Chilean Peso', '$'), 'AED': ('UAE Dirham', 'د.إ'), 'SAR': ('Saudi Riyal', '﷼'),
            'ARS': ('Argentine Peso', '$'), 'COP': ('Colombian Peso', '$'), 'RON': ('Romanian Leu', 'lei'),
            'HUF': ('Hungarian Forint', 'Ft'), 'BGN': ('Bulgarian Lev', 'лв'), 'HRK': ('Croatian Kuna', 'kn'),
            'ISK': ('Icelandic Króna', 'kr'), 'TWD': ('Taiwan Dollar', 'NT$'), 'VND': ('Vietnamese Dong', '₫'),
            'UAH': ('Ukrainian Hryvnia', '₴'), 'PKR': ('Pakistani Rupee', '₨'), 'EGP': ('Egyptian Pound', '£'),
            'NGN': ('Nigerian Naira', '₦'), 'BDT': ('Bangladeshi Taka', '৳'), 'QAR': ('Qatari Riyal', '﷼'),
            'KWD': ('Kuwaiti Dinar', 'د.ك'), 'OMR': ('Omani Rial', '﷼'), 'BHD': ('Bahraini Dinar', 'د.ب'),
            'JOD': ('Jordanian Dinar', 'د.ا'), 'KES': ('Kenyan Shilling', 'KSh'), 'MAD': ('Moroccan Dirham', 'د.م.'),
            'PEN': ('Peruvian Sol', 'S/'), 'LKR': ('Sri Lankan Rupee', 'Rs'), 'NPR': ('Nepalese Rupee', 'Rs'),
            'GHS': ('Ghanaian Cedi', '₵'), 'TZS': ('Tanzanian Shilling', 'TSh'), 'UGX': ('Ugandan Shilling', 'USh'),
            'ETB': ('Ethiopian Birr', 'Br'), 'XOF': ('West African CFA Franc', 'CFA'),
            'XAF': ('Central African CFA Franc', 'FCFA'), 'ZMW': ('Zambian Kwacha', 'ZK'),
            'BWP': ('Botswana Pula', 'P'), 'MUR': ('Mauritian Rupee', '₨'), 'NAD': ('Namibian Dollar', 'N$'),
            'AOA': ('Angolan Kwanza', 'Kz'), 'MZN': ('Mozambican Metical', 'MT'), 'RWF': ('Rwandan Franc', 'FRw'),
            'TND': ('Tunisian Dinar', 'د.ت'), 'DZD': ('Algerian Dinar', 'د.ج'), 'LYD': ('Libyan Dinar', 'ل.د'),
            'KZT': ('Kazakhstani Tenge', '₸'), 'UZS': ('Uzbekistani Som', 'soʻm'), 'GEL': ('Georgian Lari', '₾'),
            'AMD': ('Armenian Dram', '֏'), 'AZN': ('Azerbaijani Manat', '₼'), 'BYN': ('Belarusian Ruble', 'Br'),
            'MDL': ('Moldovan Leu', 'L'), 'ALL': ('Albanian Lek', 'L'), 'MKD': ('Macedonian Denar', 'ден'),
            'RSD': ('Serbian Dinar', 'дин'), 'BAM': ('Bosnia-Herzegovina Convertible Mark', 'KM'),
            'KGS': ('Kyrgyzstani Som', 'с'), 'TJS': ('Tajikistani Somoni', 'ЅМ'),
            'TMT': ('Turkmenistani Manat', 'm'), 'MNT': ('Mongolian Tögrög', '₮'),
            'AFN': ('Afghan Afghani', '؋'), 'IQD': ('Iraqi Dinar', 'ع.د'), 'IRR': ('Iranian Rial', '﷼'),
            'LBP': ('Lebanese Pound', 'ل.ل'), 'SYP': ('Syrian Pound', '£'), 'YER': ('Yemeni Rial', '﷼'),
        }
        
        # Create currency entries for ALL currencies returned by the API
        currency_count = 0
        for currency_code in rates.keys():
            if currency_code in currency_info:
                name, symbol = currency_info[currency_code]
            else:
                # For currencies not in our mapping, use generic info
                name = currency_code
                symbol = currency_code
            
            CurrencyService.get_or_create_currency(currency_code, name, symbol)
            currency_count += 1
        
        print(f"Initialized {currency_count} currencies from API")
        
        # Fetch and store initial exchange rates
        CurrencyService.update_exchange_rates('USD')
        print("Exchange rates updated successfully!")
