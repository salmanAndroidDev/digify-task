from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from .models import Account, Branch
from .serializers import AccountSerializer


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
