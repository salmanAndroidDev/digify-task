from django.db import models
from django.core.validators import MinValueValidator, \
    MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from core.models import BaseModelMixin
from django.conf import settings


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
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE,
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

    transaction_ct = models.ForeignKey(ContentType,
                                       blank=True,
                                       null=True,
                                       related_name='transaction_type',
                                       on_delete=models.CASCADE)
    transaction_id = models.UUIDField(null=True,
                                      blank=True,
                                      db_index=True)
    transaction_type = GenericForeignKey('transaction_ct', 'transaction_id')

    def __str__(self):
        return f'{self.transaction_type}'


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
        return f"{name}\t{self.amount}\tto\t{self.account.user}"


class Withdraw(BaseTransaction):
    """Withdraw model get money from the account"""


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

# TODO: CREATE Load Model
