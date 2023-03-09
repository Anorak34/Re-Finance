from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers  import check_password
from .forms import *
from .helpers import luhn, usd, currency_converter
from .models import *

valid_currencies = {'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYN', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EEK', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MRU', 'MTL', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMK ', 'ZMW'}

def main(request):
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
        return
    else:
        return render(request, 'ReFinance/quote.html', {})
    

@login_required(login_url='/login/')
def buy(request):
    if request.method == "POST":
        messages.success(request, "x shares of x bought at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/buy.html', {})


@login_required(login_url='/login/')
def sell(request):
    if request.method == "POST":
        messages.success(request, "x shares of x sold at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/sell.html', {})
    

@login_required(login_url='/login/')
def history(request):
    return render(request, 'ReFinance/history.html', {})


@login_required(login_url='/login/')
def account(request):
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
    

def test(request):
    form = CashForm()
    return render(request, 'ReFinance/test.html', {'form':form})