import aiohttp
import asyncio
import os
import requests
import time
import urllib.parse


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