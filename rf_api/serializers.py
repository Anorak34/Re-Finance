from rest_framework import serializers

from ReFinance.models import Transaction, Profile
from django.contrib.auth.models import User


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user_id', 'symbol', 'shares', 'type', 'price', 'transacted']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user','cash', 'default_currency']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', "username", "first_name", "last_name", "email",]