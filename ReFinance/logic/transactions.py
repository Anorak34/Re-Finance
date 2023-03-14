from django.db.models import Sum
from ..utilities import stocks
from ..utilities import currency
from ..models import *


class FailedPurchase(Exception):
    pass

class FailedSale(Exception):
    pass

class FailedQuote(Exception):
    pass


def buy_stock(form, request):
        if not form.is_valid():
            raise FailedPurchase("Invalid Form")
        symbol = form.cleaned_data['symbol'].upper()
        shares = form.cleaned_data['shares']
        quote = stocks.lookup(symbol)
        if not quote:
            raise FailedPurchase("Invalid Symbol")
        
        # Get User data
        user = request.user
        cash = user.userProfile.cash

        # Process transaction
        share_price = quote["price"]
        price = share_price * shares
        if price <= cash:
            Profile.addCash(user, (-price))
            Transaction.objects.create(user_id = user, symbol = symbol, shares = shares, type = 'BUY', price = share_price)
        else:
            raise FailedPurchase("Insufficient funds")
        
        return f"{shares} shares of {symbol} bought at {currency.usd(share_price)}"


def generate_sale_choices(request):
    choices = []
    user = request.user
    stocks = Transaction.objects.filter(user_id = user).values('symbol').annotate(total=(Sum('shares')))
    for stock in stocks:
        if stock['total'] != 0:
            choices.append((stock['symbol'], stock['symbol']))
    return tuple(choices)


def sell_stock(form, request):
        if not form.is_valid():
            raise FailedSale("Invalid information")
        symbol = form.cleaned_data['symbol'].upper()
        shares = form.cleaned_data['shares']
        quote = stocks.lookup(symbol)
        if not quote:
            raise FailedSale("Invalid Symbol")
        
        # Get User data
        user = request.user
        current_shares = Transaction.objects.filter(user_id = user, symbol = symbol).aggregate(TOTAL = Sum('shares'))['TOTAL']

        # Process transaction
        share_price = quote["price"]
        value = share_price * shares
        if shares > current_shares:
            raise FailedSale("You do not own enough shares")
        else:
            Profile.addCash(user, value)
            Transaction.objects.create(user_id = user, symbol = symbol, shares = -shares, type = 'SELL', price = share_price)
        
            return f"{shares} shares of {symbol} sold at {currency.usd(share_price)}"


def quote(request):
    symbol = request.POST.get("symbol")
    if not symbol:
        raise FailedQuote("Symbol is Required")  
    quote = stocks.lookup(symbol)
    if not quote:
        raise FailedQuote("Invalid Symbol")
    user = request.user
    currency_symbol = user.userProfile.default_currency
    price = currency.currency_converter(quote['price'], currency_symbol)
    return quote, price, currency_symbol