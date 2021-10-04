from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializer for user model"""
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        min_length=5)

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'password')

    def create(self, validated_data):
        """Overrider create to user encrypted password than return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user, set the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False)

    def validate(self, attrs):
        """validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'),
                            username=email, password=password)
        if not user:
            msg = _('There is no such a user with these info')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
