from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers  import check_password
from .forms import *
from .models import *
from .utilities.currency import currency_converter
from .logic import transactions
from .logic import account as a

valid_currencies = {'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYN', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EEK', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MRU', 'MTL', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMK ', 'ZMW'}

def main(request):
    if request.user.is_authenticated:   
        try:
            stocks, total, cash = a.dashboard(request)
        except:
            stocks, total, cash = None, None, None
            messages.error(request, "Error: Please try again")
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
        try:
            quote, price, currency_symbol = transactions.quote(request)
        except transactions.FailedQuote as e:
            messages.error(request, f"Error: {e}")
            return redirect('quote')
        else:
            if price['symbol'].upper() != currency_symbol.upper():
                messages.error(request, "Currency conversion error, displaying cash in USD")
            return render(request, 'ReFinance/quoted.html', {'quote':quote, 'price':price})
    else:
        return render(request, 'ReFinance/quote.html', {})
    

@login_required(login_url='/login/')
def buy(request):
    if request.method == "POST":
        # Get failure redirct from form
        form = BuyForm(request.POST)
        page = form['page'].value()
        if page != 'buy' and page != 'main':
            page = 'buy'
        # Process purchase
        try:
            bought = transactions.buy_stock(form, request)
        except transactions.FailedPurchase as e:
            messages.error(request, f"Unsuccesful Purchase: {e}")
            return redirect(page)
        else:
            messages.success(request, bought)
            return redirect('main')
    else:
        form = BuyForm(initial={'page': 'buy'})
        return render(request, 'ReFinance/buy.html', {'form':form})


@login_required(login_url='/login/')
def sell(request):
    choices = transactions.generate_sale_choices(request)

    if request.method == "POST":
        # Get failure redirct from form
        form = SellForm(choices, request.POST)
        page = form['page'].value()
        if page != 'sell' and page != 'main':
            page = 'sell'
        # Process sale
        try:
            sold = transactions.sell_stock(form, request)
        except transactions.FailedSale as e:
            messages.error(request, f"Unsuccesful Purchase: {e}")
            return redirect(page)
        else:
            messages.success(request, sold)
            return redirect('main') 
    else:
        form = SellForm(choices, initial={'page': 'sell'})
        return render(request, 'ReFinance/sell.html', {'form':form})
    

@login_required(login_url='/login/')
def history(request):
    # Get users transactions and covert the currency
    try:
        transactions, currency_symbol = a.transaction_history(request)
    except:
        transactions = None
        messages.error(request, "Error: Please try again")
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
        try:
            cash_added = a.add_cash(form, request)
        except a.FailedBalenceChange as e:
            messages.error(request, f"Unsuccesful Balence Change: {e}")
            return redirect('add_cash')
        else:
            messages.success(request, cash_added)
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