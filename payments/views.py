from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import User, Account, BankProvider, Transaction, MassPayment, MassPaymentItem
from .serializers import (
    UserSerializer, AccountSerializer, BankProviderSerializer,
    TransactionSerializer, MassPaymentCreateSerializer,
    MassPaymentListSerializer, MassPaymentDetailSerializer
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


class BankProviderViewSet(viewsets.ModelViewSet):
    queryset = BankProvider.objects.all()
    serializer_class = BankProviderSerializer
    lookup_field = 'bank_code'


class MassPaymentViewSet(viewsets.GenericViewSet):
    queryset = MassPayment.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MassPaymentCreateSerializer
        elif self.action == 'retrieve':
            return MassPaymentDetailSerializer
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
            mass_payment = MassPayment.objects.create(
                initiator_account=initiator_account,
                total_amount=total_amount,
                fee_amount=fee_amount,
                status='processing',
                description=description,
                reference_code=reference if reference else None,
                pending_count=len(recipients)
            )
            
            # Create payment items
            for recipient in recipients:
                MassPaymentItem.objects.create(
                    mass_payment=mass_payment,
                    destination_phone_number=recipient['phone_number'],
                    destination_bank_code=recipient['bank_code'],
                    amount=recipient['amount'],
                    fee_amount=fee_per_transaction
                )
            
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
                "estimated_completion_time": timezone.now() + timezone.timedelta(minutes=30)  # Example estimate
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        mass_payment = get_object_or_404(MassPayment, pk=pk)
        serializer = self.get_serializer(mass_payment)
        return Response(serializer.data)