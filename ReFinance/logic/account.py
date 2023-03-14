from django.db.models import Sum
from ..utilities import stocks as s
from ..utilities import currency
from ..utilities.card_payments import luhn
from ..models import *

class FailedBalenceChange(Exception):
    pass


def dashboard(request):
    # Get user data and currency rates
    Ustocks = []
    user = request.user
    Ustocks_temp = Transaction.objects.filter(user_id = user).values('symbol').annotate(shares=(Sum('shares')))
    for stock in Ustocks_temp:
        if stock['shares'] != 0:
            Ustocks.append(stock)
    cash = user.userProfile.cash
    currency_symbol = user.userProfile.default_currency
    try:
        currencyObj = Currency.objects.filter(expiration_date__gte = timezone.now()).order_by('id').latest('id')
    except:
        currencyObj = None

    stocks = []
    stocks_value = 0
    # Lookup all users stocks and add to list
    for stock in Ustocks:
        stocks.append(stock['symbol'])
    stocks = s.multi_lookup_async(stocks)
    # Add users stock number to the list of stock data, compute total value of each stock and all stocks, convert to user currency
    for stock, Ustock in zip(stocks, Ustocks):
        stock['shares'] = Ustock['shares']
        stock['total'] = (stock['price'] * stock['shares'])
        stocks_value += stock['total']
        stock['price'] = currency.currency_converter_mult(stock['price'], currency_symbol, currencyObj)
        stock['total'] = currency.currency_converter_mult(stock['total'], currency_symbol, currencyObj)

    total = cash + stocks_value
    total = currency.currency_converter_mult(total, currency_symbol, currencyObj)
    cash = currency.currency_converter_mult(cash, currency_symbol, currencyObj)

    return stocks, total, cash


def transaction_history(request):
    user = request.user
    transactions = Transaction.objects.filter(user_id = user).values('symbol', 'shares', 'type', 'price', 'transacted').order_by('-transacted')
    try:
        currencyObj = Currency.objects.filter(expiration_date__gte = timezone.now()).order_by('id').latest('id')
    except:
        currencyObj = None
    currency_symbol = user.userProfile.default_currency
    for transaction in transactions:
        transaction['price'] = currency.currency_converter_mult(transaction['price'], currency_symbol, currencyObj)

    return transactions, currency_symbol


def add_cash(form, request):
    if not form.is_valid():
        raise FailedBalenceChange("Please fill in all fields")
    card_number = form.cleaned_data['number'].replace(' ', '')
    try:
        int(form.cleaned_data['cvv'])
        int(card_number)
        int(form.cleaned_data['month'])
        int(form.cleaned_data['year'])
    except:
        raise FailedBalenceChange("Invalid Information")
    if int(form.cleaned_data['cvv']) < 100:
        raise FailedBalenceChange("Invalid CVV")
    if not luhn(card_number):
        raise FailedBalenceChange("Invalid Card Number")
    
    cash = float(form.cleaned_data['cash'])
    user = request.user
    Profile.addCash(user, cash)

    return f"{currency.usd(cash)} added to account"