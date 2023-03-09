from django.utils import timezone
import requests
import time
import urllib.parse
from .models import Currency
import environ
from django_q.models import Schedule

env = environ.Env()
environ.Env.read_env()

def handle_currency():
    expired_entries = Currency.objects.filter(expiration_date__lte = timezone.now())
    expired_entries.delete()

    try:
        api_key = env("API_KEY_C")
        url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        rates = response.json()
        Currency.objects.create(currencies = rates)
    except (KeyError, TypeError, ValueError):
        return None