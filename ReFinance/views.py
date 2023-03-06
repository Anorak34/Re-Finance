from django.shortcuts import render, redirect
from django.contrib import messages
import os

def main(request):
    return render(request, 'ReFinance/main.html', {})


def buy(request):
    if request.method == "POST":
        messages.success(request, "x shares of x bought at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/buy.html', {})


def history(request):
    return render(request, 'ReFinance/history.html', {})


def login(request):
    if request.method == "POST":
        return redirect('main')
    else:
        return render(request, 'ReFinance/login.html', {})


def logout(request):
    messages.success(request, "Logged out")
    return redirect('main')


def quote(request):
    if request.method == "POST":
        return
    else:
        return render(request, 'ReFinance/quote.html', {})


def register(request):
    if request.method == "POST":
        messages.success(request, "Account successfully created")
        return redirect('main')
    else:
        return render(request, 'ReFinance/register.html', {})


def sell(request):
    if request.method == "POST":
        messages.success(request, "x shares of x sold at $x")
        return redirect('main')
    else:
        return render(request, 'ReFinance/sell.html', {})


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


def account(request):
    return render(request, 'ReFinance/account.html', {})


def delete_account(request):
    if request.method == "POST":
        messages.success(request, "Account Deleted")
        return redirect('main')
    else:
        return render(request, 'ReFinance/delete_account.html', {})


def change_account_details(request):
    if request.method == "POST":
        messages.success(request, "Account details successfully altered")
        return redirect('main')
    else:
        return render(request, 'ReFinance/change_account_details.html', {})