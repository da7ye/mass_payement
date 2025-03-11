from django.db import models
import uuid
from decimal import Decimal


class User(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class BankProvider(models.Model):
    bank_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    api_endpoint = models.URLField(max_length=255)
    
    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=30, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    bank_code = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.account_number} ({self.user.phone_number})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('transfer', 'Transfer'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('pending', 'Pending'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    source_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_transactions', null=True, blank=True)
    destination_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.status}"


class MassPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partially_completed', 'Partially Completed'),
    ]
    
    initiator_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='mass_payments')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    reference_code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Mass Payment {self.reference_code} - {self.status}"


class MassPaymentItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('processing', 'Processing'),
    ]
    
    mass_payment = models.ForeignKey(MassPayment, on_delete=models.CASCADE, related_name='items')
    destination_phone_number = models.CharField(max_length=20)
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_mass_payments')
    destination_bank_code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='mass_payment_item')
    fee_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    failure_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.destination_phone_number} - {self.amount} - {self.status}"