# serializers.py
from rest_framework import serializers
from .models import PaymentTemplate, TemplateRecipient, User, Account, BankProvider, Transaction, MassPayment, MassPaymentItem


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
    

class TemplateRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateRecipient
        fields = ['id', 'phone_number', 'bank_code', 'default_amount']


class PaymentTemplateListSerializer(serializers.ModelSerializer):
    recipient_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentTemplate
        fields = ['id', 'name', 'is_active', 'created_at', 'recipient_count']
    
    def get_recipient_count(self, obj):
        return obj.recipients.count()


class PaymentTemplateDetailSerializer(serializers.ModelSerializer):
    recipients = TemplateRecipientSerializer(many=True, read_only=True)
    
    class Meta:
        model = PaymentTemplate
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at', 'recipients']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class PaymentTemplateCreateUpdateSerializer(serializers.ModelSerializer):
    recipients = TemplateRecipientSerializer(many=True)
    
    class Meta:
        model = PaymentTemplate
        fields = ['name', 'is_active', 'recipients']
    
    def create(self, validated_data):
        recipients_data = validated_data.pop('recipients')
        template = PaymentTemplate.objects.create(**validated_data)
        
        for recipient_data in recipients_data:
            TemplateRecipient.objects.create(template=template, **recipient_data)
        
        return template
    
    def update(self, instance, validated_data):
        recipients_data = validated_data.pop('recipients', None)
        
        # Update template fields
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        
        if recipients_data is not None:
            # Clear existing recipients
            instance.recipients.all().delete()
            
            # Create new recipients
            for recipient_data in recipients_data:
                TemplateRecipient.objects.create(template=instance, **recipient_data)
        
        return instance


class CreateMassPaymentFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    initiator_account_number = serializers.CharField(max_length=30)
    description = serializers.CharField(required=False, allow_blank=True)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=50)
    
    # Optional overrides for individual recipients
    recipient_overrides = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )