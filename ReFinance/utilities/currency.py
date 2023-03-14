from django.utils import timezone
import requests
import urllib.parse
from ..models import Currency
import environ
env = environ.Env()
environ.Env.read_env()


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def currency_converter(value, symbol):
    if symbol.upper() == 'USD':
        return {
            "value":value,
            "symbol":"usd"
        }
    
    currencyObj = Currency.objects.filter(expiration_date__gte = timezone.now()).order_by('id').latest('id') 
    try:
        rate = currencyObj.currencies['rates'][symbol.upper()]
    except:
        rate = None

    if rate:
        return {
            "value": float(rate) * float(value),
            "symbol": symbol
        }
    else:
        # Contact API
        try:
            api_key = env("API_KEY_C")
            url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}&symbols={urllib.parse.quote_plus(symbol.upper())}"
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException:
            return {
                "value":value,
                "symbol":"usd"
            }

        # Parse response
        try:
            rate = response.json()
            return {
                "value": float(rate["rates"][symbol.upper()]) * float(value),
                "symbol": symbol
            }
        except (KeyError, TypeError, ValueError):
            return {
                "value":value,
                "symbol":"usd"
            }


def currency_converter_mult(value, symbol, currencyObj):
    if symbol.upper() == 'USD':
        return {
            "value":value,
            "symbol":"usd"
        }
    
    try:
        rate = currencyObj.currencies['rates'][symbol.upper()]
    except:
        rate = None

    if rate:
        return {
            "value": float(rate) * float(value),
            "symbol": symbol
        }
    else:
        return {
            "value":value,
            "symbol":"usd"
        }