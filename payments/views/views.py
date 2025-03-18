from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers.payment_template_serializers import PaymentTemplateListSerializer
from ..models import (
    User, Account, BankProvider,
    MassPayment,PaymentTemplate,
)
from ..serializers.serializers import (
    UserSerializer, AccountSerializer, BankProviderSerializer,
)
from ..serializers.mass_payments_serializers import (
    MassPaymentListSerializer
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