from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
        Model serializer to open an account
    """

    class Meta:
        model = Account
        fields = ['number', 'branch', 'balance']
        extra_kwargs = {"balance": {'read_only': True}}
