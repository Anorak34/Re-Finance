# Re:Finance
#### Description:
This project is a simulated stock portfolio website built using Django that allows a user to buy and sell stocks. It uses IEX for stock data and Open Exchange Rates for currency data, if you want to use this app you can sign up for free accounts at [IEX](https://iexcloud.io/) and [Open Exchange Rates](https://openexchangerates.org/).

This project notably uses:
* Task queuing for gathering currency data from the open exchange rates API via DjangoQ.
* Async processing for API requests where multiple are made on one page via AsyncIO.
* Simple Django REST API functionality so users can query the sites database manually.
* Social Login using Django allauth for GitHub
* Dynamic styling using JavaScript and CSS
* Caching for session data using Memcached (this is currently disabled for development purposes and the app instead uses default database sessions, please set session_engine and start Memcached server to use)
