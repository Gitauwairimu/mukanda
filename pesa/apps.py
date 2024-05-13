from django.apps import AppConfig
from django.db.models.signals import post_save  # Import post_save



class FinancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pesa'

    def ready(self):
        from .models import Payment
        from .signals import check_payment_status
        post_save.connect(check_payment_status, sender=Payment)
