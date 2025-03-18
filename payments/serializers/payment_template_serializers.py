from rest_framework import serializers
from ..models import PaymentTemplate, TemplateRecipient



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