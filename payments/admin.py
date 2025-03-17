from django.contrib import admin
from .models import GroupRecipient, PaymentTemplate, RecipientGroup, TemplateRecipient, User, Account, BankProvider, Transaction, MassPayment, MassPaymentItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name')
    search_fields = ('phone_number', 'first_name', 'last_name')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'get_phone_number', 'balance', 'is_active', 'is_blocked', 'bank_code')
    list_filter = ('is_active', 'is_blocked', 'bank_code')
    search_fields = ('account_number', 'user__phone_number')
    
    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'Phone Number'

@admin.register(BankProvider)
class BankProviderAdmin(admin.ModelAdmin):
    list_display = ('bank_code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('bank_code', 'name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    date_hierarchy = 'created_at'

class MassPaymentItemInline(admin.TabularInline):
    model = MassPaymentItem
    extra = 0
    readonly_fields = ('status', 'amount', 'fee_amount', 'destination_phone_number', 'destination_bank_code')

@admin.register(MassPayment)
class MassPaymentAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'total_amount', 'status', 'success_count', 'failure_count', 'pending_count', 'created_at')
    list_filter = ('status',)
    search_fields = ('reference_code', 'initiator_account__account_number')
    date_hierarchy = 'created_at'
    inlines = [MassPaymentItemInline]

@admin.register(MassPaymentItem)
class MassPaymentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'mass_payment', 'destination_phone_number', 'destination_bank_code', 'amount', 'status')
    list_filter = ('status', 'destination_bank_code')
    search_fields = ('destination_phone_number', 'mass_payment__reference_code')
    raw_id_fields = ('mass_payment', 'transaction', 'destination_account')

class TemplateRecipientInline(admin.TabularInline):
    model = TemplateRecipient
    extra = 1  # Number of empty forms to display
    fields = ('phone_number', 'bank_code', 'name', 'default_amount', 'motive')
    search_fields = ('phone_number', 'name')

@admin.register(PaymentTemplate)
class PaymentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    inlines = [TemplateRecipientInline]

@admin.register(TemplateRecipient)
class TemplateRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'template', 'phone_number', 'bank_code', 'name', 'default_amount')
    list_filter = ('bank_code',)
    search_fields = ('phone_number', 'name', 'template__name')
    raw_id_fields = ('template',)


class GroupRecipientInline(admin.TabularInline):
    model = GroupRecipient
    extra = 1  # Number of empty forms to display
    fields = ('phone_number', 'bank_code', 'full_name', 'default_amount', 'motive', 'status')
    search_fields = ('phone_number', 'full_name')

@admin.register(RecipientGroup)
class RecipientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'status', 'created_at', 'updated_at')
    list_filter = ('is_active', 'status')
    search_fields = ('name', 'owner__phone_number')
    date_hierarchy = 'created_at'
    inlines = [GroupRecipientInline]

@admin.register(GroupRecipient)
class GroupRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'phone_number', 'bank_code', 'full_name', 'default_amount', 'status')
    list_filter = ('status', 'bank_code')
    search_fields = ('phone_number', 'full_name', 'group__name')
    raw_id_fields = ('group',)