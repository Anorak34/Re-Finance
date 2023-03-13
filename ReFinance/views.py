from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers  import check_password
from django.db.models import Sum
from .forms import *
from .helpers import luhn, usd, currency_converter, lookup, currency_converter_mult, multi_lookup_async
from .models import *

valid_currencies = {'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYN', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EEK', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MRU', 'MTL', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMK ', 'ZMW'}

def main(request):
    if request.user.is_authenticated:   
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
        stocks = multi_lookup_async(stocks)
        # Add users stock number to the list of stock data, compute total value of each stock and all stocks, convert to user currency
        for stock, Ustock in zip(stocks, Ustocks):
            stock['shares'] = Ustock['shares']
            stock['total'] = (stock['price'] * stock['shares'])
            stocks_value += stock['total']
            stock['price'] = currency_converter_mult(stock['price'], currency_symbol, currencyObj)
            stock['total'] = currency_converter_mult(stock['total'], currency_symbol, currencyObj)

        total = cash + stocks_value
        total = currency_converter_mult(total, currency_symbol, currencyObj)
        cash = currency_converter_mult(cash, currency_symbol, currencyObj)

        return render(request, 'ReFinance/dashboard.html', {'stocks':stocks, 'total':total, 'cash':cash})
    else:
        return render(request, 'ReFinance/main.html', {})


def register(request):
    if request.method == "POST":
        # Process registration form
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account successfully created")
            return redirect('main')
        messages.error(request, "Unsuccessful registration: Invalid information")
        for error in form.errors:
            messages.error(request, form.errors[error])
        return redirect('register')
    else:
        form = NewUserForm()
        return render(request, 'ReFinance/register.html', {'form':form})


def login_page(request):
    if request.method == "POST":
        # Process login form
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in as {username}")
                return redirect("main")
            else:
                messages.error(request,"Invalid username or password")
                return redirect("login")
        else:
            messages.error(request,"Invalid username or password")
            return redirect("login")
    else:
        form = LoginForm()
        return render(request, 'ReFinance/login.html', {'form':form})
    

@login_required(login_url='/login/')
def logout_page(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect('main')


@login_required(login_url='/login/')
def quote(request):
    if request.method == "POST":
        symbol = request.POST.get("symbol")
        if not symbol:
            messages.error(request, "Error: Please try again")
            return redirect('quote')  
        quote = lookup(request.POST.get("symbol"))
        if not quote:
            messages.error(request, "Invalid Symbol")
            return redirect('quote') 
        user = request.user
        currency_symbol = user.userProfile.default_currency
        price = currency_converter(quote['price'], currency_symbol)
        if price['symbol'].upper() != currency_symbol.upper():
            messages.error(request, "Currency conversion error, displaying cash in USD")
        return render(request, 'ReFinance/quoted.html', {'quote':quote, 'price':price})
    else:
        return render(request, 'ReFinance/quote.html', {})
    

@login_required(login_url='/login/')
def buy(request):
    if request.method == "POST":
        # Process Buy form
        form = BuyForm(request.POST)
        page = form['page'].value()
        if page != 'buy' and page != 'main':
            page = 'buy'
        if not form.is_valid():
            messages.error(request, "Unsuccessful Purchase: Invalid information")
            for error in form.errors:
                messages.error(request, form.errors[error])
            return redirect(page)
        symbol = form.cleaned_data['symbol'].upper()
        shares = form.cleaned_data['shares']
        quote = lookup(symbol)
        if not quote:
            messages.error(request, "Unsuccessful Purchase: Invalid Symbol")
            return redirect(page)
        
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
            messages.error(request, "Unsuccessful Purchase: Insufficient funds")
            return redirect(page)
        
        messages.success(request, f"{shares} shares of {symbol} bought at {usd(share_price)}")
        return redirect('main')
    else:
        form = BuyForm(initial={'page': 'buy'})
        return render(request, 'ReFinance/buy.html', {'form':form})


@login_required(login_url='/login/')
def sell(request):
    # Get user transactions and generate sell options
    choices = []
    user = request.user
    stocks = Transaction.objects.filter(user_id = user).values('symbol').annotate(total=(Sum('shares')))
    for stock in stocks:
        if stock['total'] != 0:
            choices.append((stock['symbol'], stock['symbol']))
    choices = tuple(choices)

    if request.method == "POST":
        # Process Sell form
        form = SellForm(choices, request.POST)
        page = form['page'].value()
        if page != 'sell' and page != 'main':
            page = 'sell'
        if not form.is_valid():
            messages.error(request, "Unsuccessful Sale: Invalid information")
            for error in form.errors:
                messages.error(request, form.errors[error])
            return redirect(page)
        symbol = form.cleaned_data['symbol'].upper()
        shares = form.cleaned_data['shares']
        quote = lookup(symbol)
        if not quote:
            messages.error(request, "Unsuccessful Sale: Invalid Symbol")
            return redirect(page)
        
        # Get User data
        current_shares = Transaction.objects.filter(user_id = user, symbol = symbol).aggregate(TOTAL = Sum('shares'))['TOTAL']

        # Process transaction
        share_price = quote["price"]
        value = share_price * shares
        if shares > current_shares:
            messages.error(request, "Unsuccessful Sale: You do not own enough shares")
            return redirect(page)
        else:
            Profile.addCash(user, value)
            Transaction.objects.create(user_id = user, symbol = symbol, shares = -shares, type = 'SELL', price = share_price)
        
            messages.success(request, f"{shares} shares of {symbol} sold at {usd(share_price)}")
            return redirect('main')
    else:
        form = SellForm(choices, initial={'page': 'sell'})
        return render(request, 'ReFinance/sell.html', {'form':form})
    

@login_required(login_url='/login/')
def history(request):
    # Get users transactions and covert the currency
    user = request.user
    transactions = Transaction.objects.filter(user_id = user).values('symbol', 'shares', 'type', 'price', 'transacted').order_by('-transacted')
    currencyObj = Currency.objects.filter(expiration_date__gte = timezone.now()).order_by('id').latest('id')
    currency_symbol = user.userProfile.default_currency
    for transaction in transactions:
        transaction['price'] = currency_converter_mult(transaction['price'], currency_symbol, currencyObj)
    if transactions:
        if transactions[0]['price']['symbol'].upper() != currency_symbol.upper():
            messages.error(request, "Currency conversion error, displaying cash in USD")
    return render(request, 'ReFinance/history.html', {'transactions':transactions})


@login_required(login_url='/login/')
def account(request):
    # Get and convert user balence
    user = request.user
    cash = user.userProfile.cash
    currency_symbol = user.userProfile.default_currency
    cash = currency_converter(cash, currency_symbol)
    if cash['symbol'].upper() != currency_symbol.upper():
        messages.error(request, "Currency conversion error, displaying cash in USD")
    return render(request, 'ReFinance/account.html', {'cash':cash})


@login_required(login_url='/login/')
def add_cash(request):
    # Process cash form
    if request.method == "POST":
        form = CashForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please fill in all fields")
            return redirect('add_cash')
        card_number = form.cleaned_data['number'].replace(' ', '')
        try:
            int(form.cleaned_data['cvv'])
            int(card_number)
            int(form.cleaned_data['month'])
            int(form.cleaned_data['year'])
        except:
            messages.error(request, "Invalid Information")
            return redirect('add_cash')
        if int(form.cleaned_data['cvv']) < 100:
            messages.error(request, "Invalid CVV")
            return redirect('add_cash')
        if not luhn(card_number):
            messages.error(request, "Invalid Card Number")
            return redirect('add_cash')
        
        cash = float(form.cleaned_data['cash'])
        user = request.user
        Profile.addCash(user, cash)
        messages.success(request, f"{usd(cash)} added to account")
        return redirect('account')
    else:
        form = CashForm()
        return render(request, 'ReFinance/addCash.html', {'form':form})


@login_required(login_url='/login/')
def change_password(request):
    if request.method == "POST":
        # Process password form
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password successfully changed")
            return redirect('account')
        messages.error(request, "Unsuccessful: Invalid information")
        for error in form.errors:
            messages.error(request, form.errors[error])
        return redirect('change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, 'ReFinance/changePass.html', {'form':form})


@login_required(login_url='/login/')
def change_account_details(request):
    if request.method == "POST":
        # Process account details form
        form = ChangeUserDetailsForm(request.POST, instance=request.user)
        currency_form = ChangeCurrencyForm(request.POST, instance=request.user.userProfile)
        if not form.is_valid():
            messages.error(request, "Unsuccessful: Invalid information")
            for error in form.errors:
                messages.error(request, form.errors[error])
            return redirect('change_account_details')
        if not currency_form.is_valid():
            messages.error(request, "Unsuccessful: Invalid information")
            for error in currency_form.errors:
                messages.error(request, currency_form.errors[error])
            return redirect('change_account_details')
        if currency_form.cleaned_data['default_currency'].upper() not in valid_currencies:
            messages.error(request, 'Invalid Currency Code')
            return redirect('change_account_details')
        form.save()
        currency_form.save()
        messages.success(request, "Account details successfully altered")
        return redirect('account')
    else:
        form = ChangeUserDetailsForm(instance=request.user)
        currency_form = ChangeCurrencyForm(instance=request.user.userProfile)
        return render(request, 'ReFinance/change_account_details.html', {'form':form, 'currency_form':currency_form})
    

@login_required(login_url='/login/')
def delete_account(request):
    if request.method == "POST":
        # Process account deletion form
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            if check_password(form.cleaned_data['password'], request.user.password):
                user = request.user
                user.delete()
                messages.success(request, "Account deleted")
                return redirect('main')
            else:
                messages.error(request, "Unsuccessful: Password Incorrect")
                return redirect('delete_account')
        messages.error(request, "Unsuccessful: Please Enter Password")
        return redirect('delete_account')
    else:
        form = DeleteAccountForm()
        return render(request, 'ReFinance/delete_account.html', {'form':form})


def view_404(request, exception=None):
    messages.error(request, "ERROR: 404 Not found")
    return redirect('main')


def view_500(request, exception=None):
    messages.error(request, "ERROR: 500 Server issue")
    return redirect('main')