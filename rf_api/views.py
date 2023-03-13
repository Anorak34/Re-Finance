from rest_framework import viewsets
from rest_framework import permissions

from .serializers import *
from ReFinance.models import Transaction, Profile
from django.contrib.auth.models import User

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Transaction.objects.all().order_by('transacted')

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return AdminTransactionSerializer
        return TransactionSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Profile.objects.all().order_by('user')

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return AdminProfileSerializer
        return ProfileSerializer
    

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    
