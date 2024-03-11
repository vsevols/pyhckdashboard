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
        'apiKey': os.environ.get('AGRAFENIN_BNCUS_API_KEY'),
        'secret': os.environ.get('AGRAFENIN_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
    })

# Символ торговли (например, 'FDUSD/USDT')
symbol = 'USDC/USDT'

# Цена и количество для ордера на покупку
price = 0.99  # Замените на актуальную цену
quantity = 20  # Количество BASE для покупки

# Создайте ордер на покупку
order = exchange.create_limit_sell_order(symbol, quantity, price)

# Выведите информацию об ордере
print(order)