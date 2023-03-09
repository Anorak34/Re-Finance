import aiohttp
import asyncio
import os
import requests
import time
import urllib.parse


valid_currencies = {'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYN', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EEK', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MRU', 'MTL', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMK ', 'ZMW'}


# API FUNCTIONS


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        attempts = 0
        max_attempts = 8
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if attempts < max_attempts:
                time.sleep(2 ** attempts)
                print(f"sleeping for {2 ** attempts} seconds")
                attempts += 1
            else:
                time.sleep(2 ** max_attempts)
                print(f"sleeping for {2 ** max_attempts} seconds")
        
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def convert_currency(value, target_currency):
    # TODO
    return None


# ASYNC FUNCTIONS


async def get_async_tasks(data_set, function):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for data in data_set:
            task = asyncio.ensure_future(function(data, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


async def lookup_async(symbol, session):
    """Look up quote for symbol."""

    try:
        attempts = 0
        max_attempts = 8
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"

            async with session.get(url) as response:
                if response.status != 429:
                    quote = await response.json()
                    break
                if attempts < max_attempts:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** max_attempts)
                    print(f"sleeping for {2 ** max_attempts} seconds")

        response.raise_for_status()
    except Exception:
        return None
    else:
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    

def multi_lookup_async(symbols):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_async_tasks(symbols, lookup_async))
    loop.run_until_complete(future)
    quote_list = future.result()
    return quote_list


# MISC FUNCTIONS


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def currency_converter(value, symbol):
    if symbol.upper() == 'USD':
        return {
            "value":value,
            "symbol":"usd"
        }
    # Contact API
    try:
        api_key = os.environ.get("API_KEY_C")
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

def luhn(number):
    sum = 0

    for i, digit in enumerate(reversed(number)):
        n = int(digit)

        if i % 2 == 0:
            sum += n
        elif n >= 5:
            sum += n * 2 - 9
        else:
            sum += n * 2

    if sum % 10 == 0:
        return True
    else:
        return False