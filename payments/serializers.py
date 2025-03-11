from rest_framework import serializers
from .models import User, Account, BankProvider, Transaction, MassPayment, MassPaymentItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name']


class BankProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankProvider
        fields = ['id', 'bank_code', 'name', 'is_active', 'api_endpoint']


class AccountSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'account_number', 'balance', 'is_active', 'is_blocked', 'bank_code', 'user', 'user_details']
        extra_kwargs = {
            'user': {'write_only': True},
        }


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'status', 'amount', 'source_account', 'destination_account', 'fee_amount', 'created_at', 'updated_at']


class MassPaymentItemCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class MassPaymentCreateSerializer(serializers.Serializer):
    initiator_account_number = serializers.CharField(max_length=30)
    recipients = MassPaymentItemCreateSerializer(many=True)
    description = serializers.CharField(required=False, allow_blank=True)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=50)


class MassPaymentItemDetailSerializer(serializers.ModelSerializer):
    bank_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MassPaymentItem
        fields = [
            'id', 'destination_phone_number', 'destination_bank_code', 'bank_name',
            'amount', 'fee_amount', 'status', 'failure_reason',
        ]
    
    def get_bank_name(self, obj):
        try:
            bank = BankProvider.objects.get(bank_code=obj.destination_bank_code)
            return bank.name
        except BankProvider.DoesNotExist:
            return "Unknown Bank"


class MassPaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MassPayment
        fields = [
            'id', 'reference_code', 'status', 'total_amount', 'success_count',
            'failure_count', 'pending_count', 'created_at', 'description',
        ]


class MassPaymentDetailSerializer(serializers.ModelSerializer):
    items = MassPaymentItemDetailSerializer(many=True, read_only=True)
    initiator_account_number = serializers.SerializerMethodField()
    contains_external_transfers = serializers.SerializerMethodField()
    
    class Meta:
        model = MassPayment
        fields = [
            'id', 'reference_code', 'initiator_account_number', 'status',
            'total_amount', 'fee_amount', 'success_count', 'failure_count',
            'pending_count', 'created_at', 'updated_at', 'description',
            'contains_external_transfers', 'items',
        ]
    
    def get_initiator_account_number(self, obj):
        return obj.initiator_account.account_number
    
    def get_contains_external_transfers(self, obj):
        bank_code = obj.initiator_account.bank_code
        return obj.items.filter(destination_bank_code__ne=bank_code).exists()