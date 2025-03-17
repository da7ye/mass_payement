from rest_framework import serializers
from ..models import  User, Account, BankProvider, MassPayment, MassPaymentItem



class MassPaymentItemCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate(self, data):
        """
        Validate that the phone_number belongs to a User and has an active Account.
        """
        phone_number = data.get('phone_number')
        bank_code = data.get('bank_code')

        try:
            # Find the user by phone_number
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"phone_number": "No user found with the provided phone number."}
            )

        try:
            # Find the active account for the user with the specified bank_code
            destination_account = Account.objects.get(
                user=user,
                bank_code=bank_code,
                is_active=True,
                is_blocked=False
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError(
                {"bank_code": "No active account found for the user with the provided bank code."}
            )

        # Add the destination_account to the validated data
        data['destination_account'] = destination_account

        return data


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
        return obj.items.filter(destination_bank_code=bank_code).exists()
    