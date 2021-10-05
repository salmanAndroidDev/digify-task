from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .models import Account, Branch, Deposit, Transaction, Withdraw, Transfer
from .permissions import IsTeller
from .serializers import AccountSerializer, SerializerCreator
from . import utils


class AuthenticationMixin:
    """Mixin for all Views that require authentication"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class OpenAccountAPIView(AuthenticationMixin, generics.CreateAPIView):
    """
        API Endpoint to an account
    """
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        """Set account user to the current user before saving it"""
        return serializer.save(user=self.request.user)


class DeleteAccountAPIView(AuthenticationMixin, generics.DestroyAPIView):
    """
        API Endpoint to remove an account
    """
    queryset = Branch.objects.all()

    def perform_destroy(self, instance):
        account = get_object_or_404(Account,
                                    user=self.request.user,
                                    branch__bank=instance.bank)
        if account.branch == instance:
            return super().perform_destroy(instance)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class BaseTransactionMixin(AuthenticationMixin, generics.CreateAPIView):
    """
        Mixin for all endpoints that deal with transaction creation
    """
    queryset = Branch.objects.all()
    model = None

    def get_object(self):
        return get_object_or_404(Branch, pk=self.kwargs.get('pk'))

    def get_serializer_class(self, *args, **kwargs):
        """Get generic serializer based on model definition"""
        return SerializerCreator.model_serializer_factory(self.model)


class DepositPaymentWithdrawMixin(BaseTransactionMixin):
    """
        Mixin for all API endpoint that are requested by teller
    """
    permission_classes = [IsAuthenticated, IsTeller]

    def create(self, request, *args, **kwargs):
        """check permissions before processing creation"""
        self.check_object_permissions(request, self.get_object())
        return super().create(request, args, kwargs)

    def apply_transaction(self, serializer, transaction_logic_method):
        account = serializer.validated_data['account']
        amount = serializer.validated_data['amount']
        if account.branch.bank == self.get_object().bank:
            if transaction_logic_method(account, amount):
                transaction_type = serializer.save()
                Transaction.objects.create(branch=self.get_object(),
                                           transaction_type=transaction_type)
                return transaction_type

        # TODO oops fix next line it returns 201!
        return Response(status=status.HTTP_409_CONFLICT)


class DepositAPIView(DepositPaymentWithdrawMixin):
    """
        API Endpoint to deposit money for an account
    """
    model = Deposit

    def perform_create(self, serializer):
        return super().apply_transaction(serializer, utils.apply_deposit)


class WithdrawAPIView(DepositPaymentWithdrawMixin):
    """
        API Endpoint to withdraw money for an account
    """
    model = Withdraw

    def perform_create(self, serializer):
        return super().apply_transaction(serializer, utils.apply_withdraw)


class TransferAPIView(DepositPaymentWithdrawMixin):
    """
        API Endpoint to transfer money for an account
    """
    model = Transfer

    def perform_create(self, serializer):
        from_account = serializer.validated_data['account']
        to_account = serializer.validated_data['to_account']
        amount = serializer.validated_data['amount']
        accounts_and_teller_has_the_same_bank = from_account.branch.bank == \
                                                to_account.branch.bank == \
                                                self.get_object().bank

        if accounts_and_teller_has_the_same_bank:
            if utils.apply_transfer(from_account, to_account, amount):
                transaction_type = serializer.save()
                Transaction.objects.create(branch=self.get_object(),
                                           transaction_type=transaction_type)
                return transaction_type

        # TODO oops fix next line it returns 201!
        return Response(status=status.HTTP_409_CONFLICT)
