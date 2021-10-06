from django.contrib import admin
from django.db.models import Count, Sum

from .models import Bank, Branch, Account, Transaction, Withdraw, \
    Transfer, Deposit, Pay


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """bank admin panel"""
    list_display = ('name', 'address', 'banker')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """branch admin panel"""

    def money(self, obj):
        """field to include total money each branch has"""
        return obj.customers.aggregate(Sum('balance'))['balance__sum']

    list_display = ('bank', 'name', 'address', 'teller', 'money')
    list_filter = ('bank',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """account admin panel"""

    def bank(self, obj):
        """bank field to display in list"""
        return obj.branch.bank

    list_display = ('user', 'number', 'balance', 'branch', 'bank')
    list_filter = ('branch',)
    ordering = ('balance',)


class BaseTransactionTypeMixin:
    """Mixin to include common fields for Withdraw, Pay, Deposit panel"""
    list_display = ('id', 'amount', 'account')
    ordering = ('amount',)


@admin.register(Withdraw)
class WithdrawAdmin(BaseTransactionTypeMixin, admin.ModelAdmin):
    """withdraw admin panel"""
    pass


@admin.register(Deposit)
class DepositAdmin(BaseTransactionTypeMixin, admin.ModelAdmin):
    """Deposit admin panel"""
    pass


@admin.register(Pay)
class PayAdmin(BaseTransactionTypeMixin, admin.ModelAdmin):
    """Pay admin panel"""
    pass


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    """transfer admin panel"""
    list_display = ('id', 'amount', 'account', 'to_account')
    ordering = ('amount',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Transaction admin panel"""
    list_display = ('id', 'transaction_type')
