from django.db import models
from django.core.validators import MinValueValidator, \
    MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import BaseModelMixin
from django.conf import settings
from .exceptions import AccountAlreadyExistError


class Bank(BaseModelMixin):
    """
        Bank model stores information related to each bank
    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    banker = models.OneToOneField(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Branch(BaseModelMixin):
    """
        Branch model stores information related to each branch
    """
    bank = models.ForeignKey(Bank,
                             on_delete=models.CASCADE,
                             related_name='branches')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    teller = models.OneToOneField(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE)

    class Meta:
        unique_together = ('bank', 'teller')

    def __str__(self):
        return f"{self.name}  ({self.bank})"


class Account(BaseModelMixin):
    """
        Account model stores information related to each customer and
        relationship he/she has with each bank
    """
    ACCOUNT_MIN_NUMBER = 1000000000000000
    ACCOUNT_MAX_NUMBER = 9999999999999999

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='accounts')

    branch = models.ForeignKey(Branch,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='customers')

    number = models.BigIntegerField(unique=True,
                                    validators=[
                                        MinValueValidator(ACCOUNT_MIN_NUMBER),
                                        MaxValueValidator(ACCOUNT_MAX_NUMBER)])

    balance = models.DecimalField(default=0.0,
                                  max_digits=10,
                                  decimal_places=2,
                                  validators=[MinValueValidator(0.0)])

    def save(self, *args, **kwargs):
        """
            Save the account only if there is no account belong to this user
            in this bank
        """

        if not Account.objects.filter(branch__bank=self.branch.bank,
                                      user=self.user).exists():
            return super().save(args, kwargs)
        else:
            raise AccountAlreadyExistError()

    def __str__(self):
        return f"{self.user} {self.branch} {self.balance}"


class Transaction(BaseModelMixin):
    """
        Transaction model to save transaction information
    """
    branch = models.ForeignKey(Branch,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='transactions')

    transfer_ct = models.ForeignKey(ContentType,
                                    blank=True,
                                    null=True,
                                    related_name='transfer_obj',
                                    on_delete=models.CASCADE)
    transfer_id = models.UUIDField(null=True,
                                   blank=True,
                                   db_index=True)
    transfer_info = GenericForeignKey('transfer_ct', 'transfer_id')

    def __str__(self):
        return str(type)


class BaseTransaction(BaseModelMixin):
    """
        Base abstract transaction that all other transactions
        inherit from
    """
    amount = models.DecimalField(max_digits=10,
                                 decimal_places=2,
                                 validators=[MinValueValidator(0.0)])

    account = models.ForeignKey(Account,
                                on_delete=models.SET_NULL,
                                null=True)

    class Meta:
        abstract: True

    def __str__(self):
        name = self.__class__.__name__  # class name
        return f"{self.amount}\tto\t{self.account}\t{name}"


class Withdraw(BaseTransaction):
    """Withdraw model get money from the account"""
    pass


class Deposit(BaseTransaction):
    """Deposit model to save money to account"""
    pass


class Pay(BaseTransaction):
    """Pay model to send money to an account"""
    pass


class Transfer(BaseTransaction):
    """Transfer money from the account to another account"""
    to_account = models.ForeignKey(Account,
                                   on_delete=models.SET_NULL,
                                   null=True)

    def __str__(self):
        name = self.__class__.__name__  # class name
        return f"{self.amount}\tfrom\t{self.account}\tto\t" \
               f"{self.to_account}\t{name}"
