from django.db import models
from django.core.validators import MinValueValidator
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='accounts')

    branch = models.ForeignKey(Branch,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='customers')

    balance = models.DecimalField(default=0.0,
                                  max_digits=10,
                                  decimal_places=2,
                                  validators=[MinValueValidator(0.0)])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
            Save the account only if there is no account belong to this user
            in this bank
        """

        if not Account.objects.filter(branch__bank=self.branch.bank,
                                      user=self.user).exists():
            return super().save(force_insert, force_update,
                                using, update_fields)
        else:
            raise AccountAlreadyExistError()

    def __str__(self):
        return f"{self.user} {self.branch} {self.balance}"
