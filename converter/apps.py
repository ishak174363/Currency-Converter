from django.apps import AppConfig


class ConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'converter'
    
    def ready(self):
        """Initialize currencies when the app starts"""
        # Import here to avoid AppRegistryNotReady error
        from .services import CurrencyService
        from .models import Currency
        
        # Only initialize if database is ready and no currencies exist
        try:
            if Currency.objects.count() == 0:
                print("Initializing currencies...")
                CurrencyService.initialize_currencies()
                print("Currencies initialized successfully!")
        except Exception as e:
            # Database might not be ready yet (during migrations)
            pass
