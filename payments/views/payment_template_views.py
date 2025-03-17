from ..models import PaymentTemplate
from ..serializers.payment_template_views import (
    PaymentTemplateListSerializer, PaymentTemplateCreateUpdateSerializer, PaymentTemplateDetailSerializer
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404



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