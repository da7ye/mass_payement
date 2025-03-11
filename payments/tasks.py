from .services import PaymentProcessor
import logging

logger = logging.getLogger(__name__)

def process_mass_payment(mass_payment_id):
    """
    Process a mass payment in the background
    @app.task
    def process_mass_payment(mass_payment_id):
        ...
    """
    try:
        logger.info(f"Starting to process mass payment {mass_payment_id}")
        PaymentProcessor.process_mass_payment(mass_payment_id)
        logger.info(f"Completed processing mass payment {mass_payment_id}")
    except Exception as e:
        logger.error(f"Error in background process for mass payment {mass_payment_id}: {str(e)}")