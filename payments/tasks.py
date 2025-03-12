# tasks.py
from .services import PaymentProcessor
import logging
"""
What Does This Code Do?
It logs when the mass payment processing starts and ends.
It calls PaymentProcessor.process_mass_payment(mass_payment_id), which runs the mass payment logic.
If an error occurs, it logs the error instead of crashing the whole system.
"""

logger = logging.getLogger(__name__)

def process_mass_payment(mass_payment_id):
    """
    Process a mass payment in the background
    """
    try:
        logger.info(f"Starting to process mass payment {mass_payment_id}")
        PaymentProcessor.process_mass_payment(mass_payment_id)
        logger.info(f"Completed processing mass payment {mass_payment_id}")
    except Exception as e:
        logger.error(f"Error in background process for mass payment {mass_payment_id}: {str(e)}")