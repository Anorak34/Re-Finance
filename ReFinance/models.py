from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userProfile')
    cash = models.FloatField(default=10000.00)
    default_currency = models.CharField(max_length=3, default='usd')

    def addCash(self, added_cash):
        self.userProfile.cash += added_cash
        self.userProfile.save()

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userProfile.save()


class Transaction(models.Model):
    class transaction_type(models.TextChoices):
        BUY = 'BUY', 'Buy'
        SELL = 'SELL', 'Sell'
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=5)
    shares = models.IntegerField()
    type = models.CharField(max_length=4, choices=transaction_type.choices)
    price = models.FloatField()
    transacted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user_id.username