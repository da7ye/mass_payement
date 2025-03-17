from rest_framework import serializers
from ..models import User, Account, BankProvider, Transaction

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
