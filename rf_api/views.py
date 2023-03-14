from rest_framework import viewsets
from rest_framework import permissions

from .serializers import *
from ReFinance.models import Transaction, Profile
from django.contrib.auth.models import User


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Transaction.objects.all().order_by('transacted')
    serializer_class = TransactionSerializer

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Profile.objects.all().order_by('user')
    serializer_class = ProfileSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    
