import ccxt
import os
from datetime import datetime
import sys

bncusProxy= 'socks5://15.164.123.59:1080/'  # AWS Seoul

# Замените на ваши ключи API
api_key = os.environ.get('STEPANOV_BNCUS_API_KEY')
api_secret = os.environ.get('STEPANOV_BNCUS_API_SECRET')

# Создание объекта для работы с биржей Binance
exchange = ccxt.binanceus({
        'apiKey': os.environ.get('STEPANOV_BNCUS_API_KEY'),
        'secret': os.environ.get('STEPANOV_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
    })

try:
    account_info = exchange.fetch_balance()
    balances = account_info['total']

    for asset, balance in balances.items():
        if balance != 0:
            print(f'{asset}: {balance}')


except ccxt.NetworkError as e:
    print(f'Ошибка сети: {e}')
except ccxt.ExchangeError as e:
    print(f'Ошибка биржи: {e}')
except Exception as e:
    print(f'Неизвестная ошибка: {e}')



