from django.db import transaction

from bank.models import Account


@transaction.atomic
def apply_deposit(account, amount):
    """Apply atomic transaction for depositing"""
    assert isinstance(account, Account)
    assert amount > 0.0
    account.balance += amount
    account.save()
    return True


@transaction.atomic
def apply_withdraw(account, amount):
    """Apply atomic transaction for withdraw"""
    assert isinstance(account, Account)
    assert amount > 0.0
    if (account.balance - amount) < 0:
        return False
    else:
        account.balance -= amount
        account.save()
        return True


@transaction.atomic
def apply_transfer(from_account, to_account, amount):
    """Apply atomic transaction for transferring money"""
    assert isinstance(from_account, Account)
    assert isinstance(to_account, Account)
    assert amount > 0.0
    if (from_account.balance - amount) < 0:
        return False
    else:
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()
        return True
