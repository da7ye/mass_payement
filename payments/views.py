import uuid
from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import (
    User, Account, BankProvider, Transaction, 
    MassPayment, MassPaymentItem, PaymentTemplate, TemplateRecipient
)
from .serializers import (
    UserSerializer, AccountSerializer, BankProviderSerializer,
    TransactionSerializer, MassPaymentCreateSerializer,
    MassPaymentListSerializer, MassPaymentDetailSerializer,
    PaymentTemplateListSerializer, PaymentTemplateDetailSerializer,
    PaymentTemplateCreateUpdateSerializer, CreateMassPaymentFromTemplateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    lookup_field = 'account_number'
    
    @action(detail=True, methods=['get'])
    def mass_payments(self, request, account_number=None):
        account = self.get_object()
        mass_payments = MassPayment.objects.filter(initiator_account=account).order_by('-created_at')
        
        page = self.paginate_queryset(mass_payments)
        if page is not None:
            serializer = MassPaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = MassPaymentListSerializer(mass_payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def payment_templates(self, request, account_number=None):
        account = self.get_object()
        templates = PaymentTemplate.objects.filter(owner=account.user).order_by('-created_at')
        
        page = self.paginate_queryset(templates)
        if page is not None:
            serializer = PaymentTemplateListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PaymentTemplateListSerializer(templates, many=True)
        return Response(serializer.data)


class BankProviderViewSet(viewsets.ModelViewSet):
    queryset = BankProvider.objects.all()
    serializer_class = BankProviderSerializer
    lookup_field = 'bank_code'


class MassPaymentViewSet(mixins.ListModelMixin, 
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = MassPayment.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MassPaymentCreateSerializer
        elif self.action == 'retrieve':
            return MassPaymentDetailSerializer
        elif self.action == 'create_from_template':
            return CreateMassPaymentFromTemplateSerializer
        return MassPaymentListSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        initiator_account_number = serializer.validated_data['initiator_account_number']
        recipients = serializer.validated_data['recipients']
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
            return Response(
                {"error": "Initiator account not found or inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total amount
        total_amount = sum(Decimal(item['amount']) for item in recipients)
        
        # Calculate fees - simplified for now, can be more complex
        fee_per_transaction = Decimal('0.50')  # Example fee
        fee_amount = fee_per_transaction * len(recipients)
        
        # Check if initiator has sufficient funds
        if initiator_account.balance < (total_amount + fee_amount):
            return Response(
                {"error": "Insufficient funds for the total amount and fees"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
                pending_count=len(recipients)
            )
            
            # Create payment items and collect them for the response
            payment_items = []
            for recipient in recipients:
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
                    "status": payment_item.status if hasattr(payment_item, 'status') else 'pending'
                })
            
            # In a real system, you would start a background task to process these payments
            # For demonstration, we'll assume starting the process here
            
            response_data = {
                "mass_payment_id": mass_payment.id,
                "reference_code": mass_payment.reference_code,
                "status": mass_payment.status,
                "total_amount": mass_payment.total_amount,
                "fee_amount": mass_payment.fee_amount,
                "created_at": mass_payment.created_at,
                "recipients_count": len(recipients),
                "external_recipients_count": sum(1 for r in recipients if r['bank_code'] != initiator_account.bank_code),
                "estimated_completion_time": timezone.now() + timezone.timedelta(minutes=30),  # Example estimate
                "recipients": payment_items  # Add the recipients to the response
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
    def retrieve(self, request, pk=None):
        mass_payment = get_object_or_404(MassPayment, pk=pk)
        serializer = self.get_serializer(mass_payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        template_id = serializer.validated_data['template_id']
        initiator_account_number = serializer.validated_data['initiator_account_number']
        description = serializer.validated_data.get('description', '')
        reference = serializer.validated_data.get('reference', '')
        recipient_overrides = serializer.validated_data.get('recipient_overrides', [])
        
        # Get the template
        try:
            template = PaymentTemplate.objects.get(id=template_id, is_active=True)
        except PaymentTemplate.DoesNotExist:
            return Response(
                {"error": "Payment template not found or inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify initiator account exists and is active
        try:
            initiator_account = Account.objects.get(
                account_number=initiator_account_number,
                is_active=True,
                is_blocked=False
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Initiator account not found or inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the template belongs to the initiator's user
        # if template.owner != initiator_account.user:
        #     return Response(
        #         {"error": "Template does not belong to the initiator"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        # Get all recipients from the template
        template_recipients = template.recipients.all()
        
        # Convert recipient overrides to a dict for easy lookup
        overrides_dict = {}
        for override in recipient_overrides:
            recipient_id = override.get('id')
            if recipient_id:
                overrides_dict[recipient_id] = override
        
        # Prepare recipients for mass payment
        payment_recipients = []
        for recipient in template_recipients:
            amount = recipient.default_amount
            
            # Apply override if it exists
            if recipient.id in overrides_dict:
                override = overrides_dict[recipient.id]
                if 'amount' in override:
                    amount = Decimal(str(override['amount']))
            
            # Skip recipients without an amount
            if amount is None:
                continue
            
            # Build recipient data
            recipient_data = {
                'phone_number': recipient.phone_number,
                'bank_code': recipient.bank_code,
                'amount': amount
            }
            
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
                
                # Add destination_account to recipient data
                recipient_data['destination_account'] = destination_account
                payment_recipients.append(recipient_data)
                
            except (User.DoesNotExist, Account.DoesNotExist):
                # Skip invalid recipients or handle as needed
                continue
        
        # If no valid recipients, return error
        if not payment_recipients:
            return Response(
                {"error": "No valid recipients found in the template"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Now create the mass payment using the validated recipients
        return self._create_mass_payment(
            initiator_account=initiator_account,
            recipients=payment_recipients,
            description=description,
            reference=reference
        )
    
    def _create_mass_payment(self, initiator_account, recipients, description='', reference=''):
        # Calculate total amount
        total_amount = sum(Decimal(str(item['amount'])) for item in recipients)
        
        # Calculate fees
        fee_per_transaction = Decimal('0.50')  # Example fee
        fee_amount = fee_per_transaction * len(recipients)
        
        # Check if initiator has sufficient funds
        if initiator_account.balance < (total_amount + fee_amount):
            return Response(
                {"error": "Insufficient funds for the total amount and fees"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
                pending_count=len(recipients)
            )
            
            # Create payment items and collect them for the response
            payment_items = []
            for recipient in recipients:
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
                    "status": payment_item.status if hasattr(payment_item, 'status') else 'pending'
                })
            
            response_data = {
                "mass_payment_id": mass_payment.id,
                "reference_code": mass_payment.reference_code,
                "status": mass_payment.status,
                "total_amount": mass_payment.total_amount,
                "fee_amount": mass_payment.fee_amount,
                "created_at": mass_payment.created_at,
                "recipients_count": len(recipients),
                "external_recipients_count": sum(1 for r in recipients if r['bank_code'] != initiator_account.bank_code),
                "estimated_completion_time": timezone.now() + timezone.timedelta(minutes=30),
                "recipients": payment_items
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)


class PaymentTemplateViewSet(viewsets.ModelViewSet):
    queryset = PaymentTemplate.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentTemplateCreateUpdateSerializer
        elif self.action == 'retrieve':
            return PaymentTemplateDetailSerializer
        return PaymentTemplateListSerializer
    
    def get_queryset(self):
        # # Filter templates to only show those owned by the current user
        # user = self.request.user
        # if user.is_authenticated:
        #     # Assuming you have authentication set up
        #     # In a test environment, you might want to remove this filter
        #     return PaymentTemplate.objects.filter(owner=user)
        # return PaymentTemplate.objects.none()
        
        # for now, return all templates
        return PaymentTemplate.objects.all()
    
    # def perform_create(self, serializer):
    #     # Set the owner to the current user
    #     serializer.save(owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        template = serializer.instance
        
        # Return the detail view of the created template
        detail_serializer = PaymentTemplateDetailSerializer(template)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return the detail view of the updated template
        detail_serializer = PaymentTemplateDetailSerializer(instance)
        return Response(detail_serializer.data)