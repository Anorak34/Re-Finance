from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import *


def main(request):
    return render(request, 'ReFinance/main.html', {})


def register(request):
    if request.method == "POST":
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
    

def logout_page(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect('main')


def quote(request):
    if request.method == "POST":
        return
    else:
        return render(request, 'ReFinance/quote.html', {})
    

def buy(request):
    if request.method == "POST":
        messages.success(request, "x shares of x bought at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/buy.html', {})


def sell(request):
    if request.method == "POST":
        messages.success(request, "x shares of x sold at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/sell.html', {})
    

def history(request):
    return render(request, 'ReFinance/history.html', {})


def account(request):
    return render(request, 'ReFinance/account.html', {})


def add_cash(request):
    if request.method == "POST":
        messages.success(request, "$x added to account")
        return redirect('account')
    else:
        return render(request, 'ReFinance/addCash.html', {})


def change_password(request):
    if request.method == "POST":
        messages.success(request, "Password successfully changed")
        return redirect('account')
    else:
        return render(request, 'ReFinance/changePass.html', {})


def change_account_details(request):
    if request.method == "POST":
        messages.success(request, "Account details successfully altered")
        return redirect('main')
    else:
        return render(request, 'ReFinance/change_account_details.html', {})
    

def delete_account(request):
    if request.method == "POST":
        messages.success(request, "Account Deleted")
        return redirect('main')
    else:
        return render(request, 'ReFinance/delete_account.html', {})