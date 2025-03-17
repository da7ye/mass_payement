from django.core.management.base import BaseCommand
from payments.models import User, Account, BankProvider, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates demo data for testing the mass payment service'

    def handle(self, *args, **options):
        # Create bank providers
        self.stdout.write('Creating bank providers...')
        banks = [
            ('SEDAD', 'Sedad Bank', 'https://api.sedad.test.com'),
            ('BIMBANK', 'Bimbank Bank', 'https://api.bimbank.test.com'),
            ('BANKILY', 'bankily Bank', 'https://api.bankily.test.com'),
        ]
        
        for code, name, api in banks:
            BankProvider.objects.get_or_create(
                bank_code=code,
                defaults={
                    'name': name,
                    'is_active': True,
                    'api_endpoint': api
                }
            )
        
        # Create test users
        self.stdout.write('Creating test users...')
        users = [
            ('20593670', 'Med yahya', 'Mohamed'),
            ('42563512', 'Selemhe', 'Med salem'),
            ('36459515', 'Aichetou', 'Mohamed'),
            ('26456565', 'Ahmed', 'Lemine'),
            ('26594815', 'Sidi', 'Lemine'),
        ]
        
        for phone, first, last in users:
            User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'first_name': first,
                    'last_name': last
                }
            )
        
        # Create accounts
        self.stdout.write('Creating accounts...')
        Med = User.objects.get(phone_number='20593670')
        Selemhe = User.objects.get(phone_number='42563512')
        Aichetou = User.objects.get(phone_number='36459515')
        Ahmed = User.objects.get(phone_number='26456565')
        Sidi = User.objects.get(phone_number='26594815')
        
        accounts = [
            (Med, 'ACC001', Decimal('10000.00'), 'SEDAD'),
            (Selemhe, 'ACC002', Decimal('5000.00'), 'SEDAD'),
            (Aichetou, 'ACC003', Decimal('7500.00'), 'BIMBANK'),
            (Ahmed, 'ACC004', Decimal('3000.00'), 'BIMBANK'),
            (Sidi, 'ACC005', Decimal('12000.00'), 'BANKILY'),
        ]
        
        for user, acc_num, balance, bank_code in accounts:
            Account.objects.get_or_create(
                account_number=acc_num,
                defaults={
                    'user': user,
                    'balance': balance,
                    'is_active': True,
                    'is_blocked': False,
                    'bank_code': bank_code
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created demo data'))