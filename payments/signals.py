
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MassPayment
from .tasks import process_mass_payment
import threading

@receiver(post_save, sender=MassPayment)
def start_mass_payment_processing(sender, instance, created, **kwargs):
    """
    Start processing a mass payment when it's created
    """
    if created:
        # In a real production environment, you would use Celery or another task queue
        # For this example, we're using a simple thread (not recommended for production)
        threading.Thread(target=process_mass_payment, args=(instance.id,)).start()