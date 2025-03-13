# services.py
from django.db import transaction
from decimal import Decimal
from .models import Account, Transaction, MassPayment, MassPaymentItem, BankProvider
import logging

logger = logging.getLogger(__name__)

"""
    The script processes mass payments consisting of multiple payment items.
    It handles both internal transfers (between accounts in the system)
    and external transfers (to accounts outside the system,likely using a bank API).
    It ensures transactional integrity using Django’s transaction.atomic() to prevent inconsistent data states.
"""

class PaymentProcessor:
    @staticmethod
    def process_mass_payment(mass_payment_id):
        """
        Process all items in a mass payment
        """
        try:
            mass_payment = MassPayment.objects.select_for_update().get(id=mass_payment_id)
            
            # Skip if already completed or failed
            if mass_payment.status in ['completed', 'failed']:
                return
            
            # Update status to processing
            mass_payment.status = 'processing'
            mass_payment.save()
            
            # Get all pending payment items
            payment_items = MassPaymentItem.objects.filter(
                mass_payment=mass_payment,
                status='pending'
            )
            
            # Process each payment item
            for item in payment_items:
                PaymentProcessor._process_payment_item(mass_payment, item)
            
            # Update mass payment status
            PaymentProcessor._update_mass_payment_status(mass_payment)
            
        except Exception as e:
            logger.error(f"Error processing mass payment {mass_payment_id}: {str(e)}")
            # In case of error, mark as failed if possible
            try:
                mass_payment.status = 'failed'
                mass_payment.save()
            except:
                pass
    
    @staticmethod
    def _process_payment_item(mass_payment, payment_item):
        """
        Process a single payment item
        """
        with transaction.atomic():
            try:
                # Mark as processing
                payment_item.status = 'processing'
                payment_item.save()
                
                # Validate initiator has sufficient funds
                initiator_account = mass_payment.initiator_account
                if initiator_account.balance < (payment_item.amount + payment_item.fee_amount):
                    payment_item.status = 'failed'
                    payment_item.failure_reason = "Insufficient funds"
                    payment_item.save()
                    
                    # Update counters
                    mass_payment.pending_count -= 1
                    mass_payment.failure_count += 1
                    mass_payment.save()
                    return
                
                # Try to find destination account
                destination_account = None
                try:
                    # Find user by phone number
                    destination_user = initiator_account.user.__class__.objects.get(
                        phone_number=payment_item.destination_phone_number
                    )
                    
                    # Find corresponding account 
                    destination_account = Account.objects.filter(
                        user=destination_user,
                        bank_code=payment_item.destination_bank_code,
                        is_active=True,
                        is_blocked=False
                    ).first()
                except:
                    # Account not found - would be an external transfer
                    pass
                
                # Handle based on internal vs external transfer
                if destination_account:
                    # Internal transfer
                    success = PaymentProcessor._process_internal_transfer(
                        payment_item, initiator_account, destination_account
                    )
                else:
                    # External transfer - would go to external API
                    success = PaymentProcessor._process_external_transfer(
                        payment_item, initiator_account
                    )
                
                # Update counters
                mass_payment.pending_count -= 1
                if success:
                    mass_payment.success_count += 1
                else:
                    mass_payment.failure_count += 1
                mass_payment.save()
                
            except Exception as e:
                logger.error(f"Error processing payment item {payment_item.id}: {str(e)}")
                payment_item.status = 'failed'
                payment_item.failure_reason = str(e)
                payment_item.save()
                
                # Update counters
                mass_payment.pending_count -= 1
                mass_payment.failure_count += 1
                mass_payment.save()
    
    @staticmethod
    def _process_internal_transfer(payment_item, source_account, destination_account):
        """
        Process internal transfer between accounts
        """
        try:
            # Create transaction
            transaction = Transaction.objects.create(
                transaction_type='transfer',
                status='pending',
                amount=payment_item.amount,
                source_account=source_account,
                destination_account=destination_account,
                fee_amount=payment_item.fee_amount
            )
            
            # Update account balances
            source_account.balance -= (payment_item.amount + payment_item.fee_amount)
            destination_account.balance += payment_item.amount
            
            source_account.save()
            destination_account.save()
            
            # Update transaction
            transaction.status = 'success'
            transaction.save()
            
            # Link transaction to payment item
            payment_item.transaction = transaction
            payment_item.status = 'success'
            payment_item.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Internal transfer failed: {str(e)}")
            payment_item.status = 'failed'
            payment_item.failure_reason = f"Internal transfer failed: {str(e)}"
            payment_item.save()
            return False
    
    @staticmethod
    def _process_external_transfer(payment_item, source_account):
        """
        Process transfer to external bank
        """
        try:
            # Check if bank provider exists
            try:
                bank_provider = BankProvider.objects.get(
                    bank_code=payment_item.destination_bank_code,
                    is_active=True
                )
            except BankProvider.DoesNotExist:
                payment_item.status = 'failed'
                payment_item.failure_reason = "Bank provider not supported"
                payment_item.save()
                return False
            
            # In a real system, you would make an API call to the bank_provider.api_endpoint
            # For this example, we'll simulate a successful external transfer
            
            # Create transaction record
            transaction = Transaction.objects.create(
                transaction_type='transfer',
                status='pending',
                amount=payment_item.amount,
                source_account=source_account,
                destination_account=None,  # External account
                fee_amount=payment_item.fee_amount
            )
            
            # Deduct from source account
            source_account.balance -= (payment_item.amount + payment_item.fee_amount)
            source_account.save()
            
            # Update transaction
            transaction.status = 'success'
            transaction.save()
            
            # Link transaction to payment item
            payment_item.transaction = transaction
            payment_item.status = 'success'
            payment_item.save()
            
            return True
            
        except Exception as e:
            logger.error(f"External transfer failed: {str(e)}")
            payment_item.status = 'failed'
            payment_item.failure_reason = f"External transfer failed: {str(e)}"
            payment_item.save()
            return False
    
    @staticmethod
    def _update_mass_payment_status(mass_payment):
        """
        Update the overall status of a mass payment
        """
        if mass_payment.pending_count == 0:
            if mass_payment.failure_count == 0:
                mass_payment.status = 'completed'
            elif mass_payment.success_count == 0:
                mass_payment.status = 'failed'
            else:
                mass_payment.status = 'partially_completed'
            mass_payment.save()