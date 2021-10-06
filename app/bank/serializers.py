from rest_framework import serializers
from .models import Account, BaseTransaction, Transaction, Branch


class BranchSerializer(serializers.ModelSerializer):
    """
        Model serializer to create branch
    """

    class Meta:
        model = Branch
        fields = ('name', 'address', 'teller','bank')
        extra_kwargs = {"bank": {'read_only': True}}


class AccountSerializer(serializers.ModelSerializer):
    """
        Model serializer to open an account
    """

    class Meta:
        model = Account
        fields = ['number', 'branch', 'balance']
        extra_kwargs = {"balance": {'read_only': True}}

    def create(self, validated_data):
        """
            Save the account only if there is no account belong to this user
            in this bank
        """
        user = validated_data['user']
        branch = validated_data['branch']
        if not Account.objects.filter(branch__bank=branch.bank,
                                      user=user).exists():
            return super().create(validated_data)
        else:
            raise serializers.ValidationError()


class SerializerCreator:
    """
        Creator class, to create models serializers for Transaction types
        in a generic way
    """

    @staticmethod
    def model_serializer_factory(model):
        """Factory to create generic ModelSerializer"""
        assert issubclass(model, BaseTransaction)
        Meta = type('Meta',
                    (object,),
                    {'model': model,
                     'fields': '__all__',
                     'ref_name': model.__name__,  # add this field for swagger
                     })

        Serializer = type('TransactionTypeSerializer',
                          (serializers.ModelSerializer,),
                          {'Meta': Meta})
        return Serializer


class TransactionSerializer(serializers.ModelSerializer):
    """
        Transaction Serializer to serialize transactions
    """

    class Meta:
        model = Transaction
        fields = ('branch', 'transaction_type')
