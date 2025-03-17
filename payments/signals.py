# signals.py:

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MassPayment, RecipientGroup
from .tasks import process_mass_payment, process_recipient_group
import threading
from django.db import transaction


"""
signals.py:
sets up an automatic trigger that activates when a new MassPayment is created
"""
@receiver(post_save, sender=MassPayment)
def start_mass_payment_processing(sender, instance, created, **kwargs):
    """
    Start processing a mass payment when it's created
    """
    if created:
        # Use transaction.on_commit to ensure the transaction is complete
        # before starting the background processing
        transaction.on_commit(
            lambda: threading.Thread(
                target=process_mass_payment, 
                args=(instance.id,),
                daemon=False
            ).start()
        )



@receiver(post_save, sender=RecipientGroup)
def start_recipient_group_processing(sender, instance, created, **kwargs):
    """
    Start processing a recipient group when it's created.
    """
    if created:
        transaction.on_commit(
            lambda: threading.Thread(
                target=process_recipient_group, 
                args=(instance.id,),
                daemon=False
            ).start()
        )