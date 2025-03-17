from payments.services.recipient_group_services import RecipientGroupProcessor
from ..models import Account, GroupRecipient, MassPayment, MassPaymentItem, RecipientGroup, User
from ..serializers.group_recipiants_serializers import (
    AddRecipientToGroupSerializer, CreateMassPaymentFromGroupSerializer, RecipientGroupCreateUpdateSerializer, RecipientGroupDetailSerializer, RecipientGroupListSerializer, RecipientValidationSerializer, UploadRecipientsCSVSerializer
)
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from io import TextIOWrapper
import csv



class RecipientGroupViewSet(viewsets.ModelViewSet):
    queryset = RecipientGroup.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'upload_recipients_csv':
            return UploadRecipientsCSVSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return RecipientGroupCreateUpdateSerializer
        elif self.action == 'retrieve':
            return RecipientGroupDetailSerializer
        elif self.action == 'validate_recipient':
            return RecipientValidationSerializer
        elif self.action == 'add_recipient':
            return AddRecipientToGroupSerializer
        elif self.action == 'create_mass_payment':
            return CreateMassPaymentFromGroupSerializer
        elif self.action == 'process_recipients':
            return None  # No serializer needed for this action
        return RecipientGroupListSerializer
    
    def get_queryset(self):
        # Filter groups to only show those owned by the current user
        # user = self.request.user
        # if user.is_authenticated:
        #     return RecipientGroup.objects.filter(owner=user)
        # return RecipientGroup.objects.none()
    
        # For now, return all groups
        return RecipientGroup.objects.all()
    
    def perform_create(self, serializer):
        # Set the owner to the current user
        # serializer.save(owner=self.request.user)
        serializer.save()  # Save without setting the owner

    @action(detail=False, methods=['post'])
    def validate_recipient(self, request):
        """
        Validate if a recipient exists and return their full name.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        bank_code = serializer.validated_data['bank_code']
        
        try:
            # Find the user by phone_number
            user = User.objects.get(phone_number=phone_number)
            
            # Check if the user has an active account with the specified bank_code
            try:
                account = Account.objects.get(
                    user=user,
                    bank_code=bank_code,
                    is_active=True,
                    is_blocked=False
                )
                
                return Response({
                    "exists": True,
                    "full_name": f"{user.first_name} {user.last_name}",
                    "account_number": account.account_number
                })
                
            except Account.DoesNotExist:
                return Response({
                    "exists": False,
                    "error": "No active account found for this user with the provided bank code"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                "exists": False,
                "error": "User not found with the provided phone number"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_recipient(self, request, pk=None):
        """
        Add a validated recipient to a group.
        """
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        bank_code = serializer.validated_data['bank_code']
        default_amount = serializer.validated_data.get('default_amount')
        motive = serializer.validated_data.get('motive', '')
        
        # First validate the recipient
        try:
            user = User.objects.get(phone_number=phone_number)
            
            try:
                account = Account.objects.get(
                    user=user,
                    bank_code=bank_code,
                    is_active=True,
                    is_blocked=False
                )
                
                # Check if recipient already exists in this group
                if GroupRecipient.objects.filter(
                    group=group,
                    phone_number=phone_number,
                    bank_code=bank_code
                ).exists():
                    return Response({
                        "success": False,
                        "error": "This recipient already exists in the group"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Add the recipient to the group
                recipient = GroupRecipient.objects.create(
                    group=group,
                    phone_number=phone_number,
                    bank_code=bank_code,
                    full_name=f"{user.first_name} {user.last_name}",
                    default_amount=default_amount,
                    motive=motive,
                    status='pending'  # Set initial status to 'pending'
                )
                
                return Response({
                    "success": True,
                    "id": recipient.id,
                    "full_name": recipient.full_name,
                    "phone_number": recipient.phone_number,
                    "bank_code": recipient.bank_code,
                    "default_amount": recipient.default_amount,
                    "motive": recipient.motive,
                    "status": recipient.status
                })
                
            except Account.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "No active account found for this user with the provided bank code"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found with the provided phone number"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_recipients(self, request, pk=None):
        """
        Process all recipients in the group.
        """
        group = self.get_object()
        try:
            RecipientGroupProcessor.process_group_recipients(group.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




    @action(detail=True, methods=['post'])
    def create_mass_payment(self, request, pk=None):
        """
        Create a mass payment from a recipient group.
        """
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        initiator_account_number = serializer.validated_data['initiator_account_number']
        description = serializer.validated_data.get('description', '')
        reference = serializer.validated_data.get('reference', '')
        
        # Verify initiator account exists and is active
        try:
            initiator_account = Account.objects.get(
                account_number=initiator_account_number,
                is_active=True,
                is_blocked=False
            )
        except Account.DoesNotExist:
            return Response({
                "error": "Initiator account not found or inactive"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the group belongs to the initiator's user
        # if group.owner != initiator_account.user:
        #     return Response({
        #         "error": "Recipient group does not belong to the account owner"
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all recipients from the group
        group_recipients = group.recipients.all()
        
        # If no recipients, return error
        if not group_recipients.exists():
            return Response({
                "error": "No recipients found in the group"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare recipients for mass payment
        payment_recipients = []
        for recipient in group_recipients:
            # Skip recipients without an amount
            if recipient.default_amount is None:
                continue
            
            # Validate recipient data
            try:
                # Find the user by phone_number
                user = User.objects.get(phone_number=recipient.phone_number)
                
                # Find active account for user with the specified bank_code
                destination_account = Account.objects.get(
                    user=user,
                    bank_code=recipient.bank_code,
                    is_active=True,
                    is_blocked=False
                )
                
                # Skip if destination account is the same as initiator account
                if destination_account.account_number == initiator_account.account_number:
                    continue
                
                # Add to payment recipients
                payment_recipients.append({
                    'phone_number': recipient.phone_number,
                    'bank_code': recipient.bank_code,
                    'amount': recipient.default_amount,
                    'destination_account': destination_account,
                    'motive': recipient.motive
                })
                
            except (User.DoesNotExist, Account.DoesNotExist):
                # Skip invalid recipients
                continue
        
        # If no valid recipients, return error
        if not payment_recipients:
            return Response({
                "error": "No valid recipients found in the group"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Now create the mass payment
        total_amount = sum(recipient['amount'] for recipient in payment_recipients)
        fee_per_transaction = Decimal('0.50')  # Example fee
        fee_amount = fee_per_transaction * len(payment_recipients)
        
        # Check if initiator has sufficient funds
        if initiator_account.balance < (total_amount + fee_amount):
            return Response({
                "error": "Insufficient funds for the total amount and fees"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the mass payment
        with transaction.atomic():
            # Generate a reference code if none provided
            if not reference:
                reference = f"MP{uuid.uuid4().hex[:8].upper()}"
            
            mass_payment = MassPayment.objects.create(
                initiator_account=initiator_account,
                total_amount=total_amount,
                fee_amount=fee_amount,
                status='processing',
                description=description,
                reference_code=reference,
                pending_count=len(payment_recipients)
            )
            
            # Create payment items
            payment_items = []
            for recipient in payment_recipients:
                payment_item = MassPaymentItem.objects.create(
                    mass_payment=mass_payment,
                    destination_phone_number=recipient['phone_number'],
                    destination_account=recipient['destination_account'],
                    destination_bank_code=recipient['bank_code'],
                    amount=recipient['amount'],
                    fee_amount=fee_per_transaction
                )
                payment_items.append({
                    "id": payment_item.id,
                    "phone_number": payment_item.destination_phone_number,
                    "bank_code": payment_item.destination_bank_code,
                    "amount": payment_item.amount,
                    "fee_amount": payment_item.fee_amount,
                    "status": payment_item.status
                })
            
            response_data = {
                "mass_payment_id": mass_payment.id,
                "reference_code": mass_payment.reference_code,
                "status": mass_payment.status,
                "total_amount": str(total_amount),
                "fee_amount": str(fee_amount),
                "created_at": mass_payment.created_at,
                "recipients_count": len(payment_recipients),
                "external_recipients_count": sum(
                    1 for r in payment_recipients 
                    if r['bank_code'] != initiator_account.bank_code
                ),
                "estimated_completion_time": timezone.now() + timezone.timedelta(minutes=30),
                "recipients": payment_items
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)    

    
    @action(detail=True, methods=['post'])
    def upload_recipients_csv(self, request, pk=None):
        group = self.get_object()
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response({"error": "No CSV file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)
            
            total_records = 0
            successful_records = 0
            failed_records = []

            with transaction.atomic():
                for row in reader:
                    total_records += 1
                    
                    try:
                        # Extract data from CSV
                        phone_number = row.get('phone_number')
                        amount = row.get('amount')
                        motive = row.get('motive', '')
                        
                        # Validate required fields
                        if not phone_number or not amount:
                            failed_records.append({
                                "row": row,
                                "error": "Missing required fields (phone_number or amount)"
                            })
                            continue
                        
                        # Find the user by phone number
                        user = User.objects.get(phone_number=phone_number)
                        
                        # Get the user's account
                        accounts = Account.objects.filter(
                            user=user,
                            is_active=True,
                            is_blocked=False
                        )
                        
                        if not accounts.exists():
                            failed_records.append({
                                "phone_number": phone_number,
                                "error": "No active account found for this user"
                            })
                            continue
                        
                        # Use the first active account found
                        account = accounts.first()
                        bank_code = account.bank_code
                        
                        # Check if recipient already exists in the group
                        if GroupRecipient.objects.filter(
                            group=group,
                            phone_number=phone_number,
                            bank_code=bank_code
                        ).exists():
                            failed_records.append({
                                "phone_number": phone_number,
                                "error": "Recipient already exists in this group"
                            })
                            continue

                        # Add recipient to group
                        GroupRecipient.objects.create(
                            group=group,
                            phone_number=phone_number,
                            bank_code=bank_code,
                            full_name=f"{user.first_name} {user.last_name}",
                            default_amount=Decimal(amount),
                            motive=motive,
                            status='validated'
                        )
                        successful_records += 1
                        
                    except User.DoesNotExist:
                        failed_records.append({
                            "phone_number": phone_number,
                            "error": "User not found with this phone number"
                        })
                    except Exception as e:
                        failed_records.append({
                            "phone_number": phone_number if 'phone_number' in locals() else "Unknown",
                            "error": str(e)
                        })

            # Calculate success percentage
            success_percentage = (successful_records / total_records * 100) if total_records > 0 else 0
            
            # Update group status
            if successful_records == total_records:
                group.status = 'completed'
            elif successful_records > 0:
                group.status = 'partially_completed'
            else:
                group.status = 'failed'
            group.save()
            
            # Prepare response message
            message = f"{successful_records} successful out of {total_records}! ({success_percentage:.1f}%)"
            
            return Response({
                "message": message,
                "successful_count": successful_records,
                "total_count": total_records,
                "success_percentage": f"{success_percentage:.1f}%",
                "failed_records": failed_records if failed_records else None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)