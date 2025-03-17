from django.db import transaction
from ..models import Account, GroupRecipient, RecipientGroup, User
from .services import logger

class RecipientGroupProcessor:
    @staticmethod
    def create_recipient_group(name, owner):
        """
        Create a new recipient group.
        """
        try:
            with transaction.atomic():
                group = RecipientGroup.objects.create(
                    name=name,
                    owner=owner
                )
                logger.info(f"Created recipient group {group.id}")
                return group
        except Exception as e:
            logger.error(f"Error creating recipient group: {str(e)}")
            raise

    @staticmethod
    def validate_recipient(phone_number, bank_code):
        """
        Validate if a recipient exists and return their full name.
        """
        try:
            user = User.objects.get(phone_number=phone_number)
            account = Account.objects.get(
                user=user,
                bank_code=bank_code,
                is_active=True,
                is_blocked=False
            )
            return {
                "exists": True,
                "full_name": f"{user.first_name} {user.last_name}",
                "account_number": account.account_number
            }
        except User.DoesNotExist:
            return {
                "exists": False,
                "error": "User not found with the provided phone number"
            }
        except Account.DoesNotExist:
            return {
                "exists": False,
                "error": "No active account found for the user with the provided bank code"
            }

    @staticmethod
    def add_recipient_to_group(group_id, phone_number, bank_code, default_amount, motive):
        """
        Add a validated recipient to a group.
        """
        try:
            with transaction.atomic():
                group = RecipientGroup.objects.get(id=group_id)
                user = User.objects.get(phone_number=phone_number)
                account = Account.objects.get(
                    user=user,
                    bank_code=bank_code,
                    is_active=True,
                    is_blocked=False
                )

                # Check if recipient already exists in the group
                if GroupRecipient.objects.filter(
                    group=group,
                    phone_number=phone_number,
                    bank_code=bank_code
                ).exists():
                    return {
                        "success": False,
                        "error": "Recipient already exists in the group"
                    }

                # Add the recipient to the group
                recipient = GroupRecipient.objects.create(
                    group=group,
                    phone_number=phone_number,
                    bank_code=bank_code,
                    full_name=f"{user.first_name} {user.last_name}",
                    default_amount=default_amount,
                    motive=motive,
                    status='validated'  # Set status to 'validated'
                )
                logger.info(f"Added recipient {recipient.id} to group {group.id}")
                return {
                    "success": True,
                    "recipient_id": recipient.id
                }
        except Exception as e:
            logger.error(f"Error adding recipient to group: {str(e)}")
            raise

    @staticmethod
    def process_group_recipients(group_id):
        """
        Process all recipients in a group.
        """
        try:
            group = RecipientGroup.objects.get(id=group_id)
            recipients = group.recipients.filter(status='pending')

            for recipient in recipients:
                RecipientGroupProcessor._process_recipient(recipient)

            # Update group status
            if group.recipients.filter(status='failed').exists():
                group.status = 'partially_completed'
            else:
                group.status = 'completed'
            group.save()

        except Exception as e:
            logger.error(f"Error processing group recipients: {str(e)}")
            group.status = 'failed'
            group.save()
            raise

    @staticmethod
    def _process_recipient(recipient):
        """
        Process a single recipient.
        """
        try:
            with transaction.atomic():
                # Validate recipient
                validation_result = RecipientGroupProcessor.validate_recipient(
                    recipient.phone_number,
                    recipient.bank_code
                )

                if not validation_result['exists']:
                    recipient.status = 'failed'
                    recipient.failure_reason = validation_result.get('error', 'Validation failed')
                    recipient.save()
                    return

                # If validation passes, mark as validated
                recipient.status = 'validated'
                recipient.save()

        except Exception as e:
            logger.error(f"Error processing recipient {recipient.id}: {str(e)}")
            recipient.status = 'failed'
            recipient.failure_reason = str(e)
            recipient.save()