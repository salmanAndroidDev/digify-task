from django.contrib import admin
from .models import Bank, Branch, Account, Transaction, Withdraw,\
    Transfer, Deposit, Pay

admin.site.register(Bank)
admin.site.register(Branch)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Withdraw)
admin.site.register(Transfer)
admin.site.register(Deposit)
admin.site.register(Pay)
