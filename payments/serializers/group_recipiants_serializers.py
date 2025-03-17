from rest_framework import serializers
from ..models import GroupRecipient, PaymentTemplate, RecipientGroup, TemplateRecipient, User, Account, BankProvider, Transaction, MassPayment, MassPaymentItem


class GroupRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRecipient
        fields = ['id', 'phone_number', 'bank_code', 'full_name', 'default_amount', 'motive']


class RecipientGroupListSerializer(serializers.ModelSerializer):
    recipient_count = serializers.SerializerMethodField()
    recipients = GroupRecipientSerializer(many=True, required=False)
    
    class Meta:
        model = RecipientGroup
        fields = ['id', 'name', 'is_active', 'created_at', 'recipient_count', 'recipients', 'status']
    
    def get_recipient_count(self, obj):
        return obj.recipients.count()


class RecipientGroupDetailSerializer(serializers.ModelSerializer):
    recipients = GroupRecipientSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecipientGroup
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at', 'recipients']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class RecipientGroupCreateUpdateSerializer(serializers.ModelSerializer):
    # recipients = GroupRecipientSerializer(many=True, required=False)
    
    class Meta:
        model = RecipientGroup
        fields = ['id','name', 'is_active', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        recipients_data = validated_data.pop('recipients', [])
        group = RecipientGroup.objects.create(**validated_data)
        
        for recipient_data in recipients_data:
            GroupRecipient.objects.create(group=group, **recipient_data)
        
        return group
    
    def update(self, instance, validated_data):
        recipients_data = validated_data.pop('recipients', None)
        
        # Update group fields
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        
        if recipients_data is not None:
            # Clear existing recipients
            instance.recipients.all().delete()
            
            # Create new recipients
            for recipient_data in recipients_data:
                GroupRecipient.objects.create(group=instance, **recipient_data)
        
        return instance


class RecipientValidationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=10)


class AddRecipientToGroupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=10)
    default_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    motive = serializers.CharField(max_length=255, required=False, allow_blank=True)


class CreateMassPaymentFromGroupSerializer(serializers.Serializer):
    initiator_account_number = serializers.CharField(max_length=30)
    description = serializers.CharField(required=False, allow_blank=True)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=50)

class UploadRecipientsCSVSerializer(serializers.Serializer):
    file = serializers.FileField()