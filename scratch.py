import ccxt
import os
from datetime import datetime
import sys

bncusProxy= 'socks5://15.164.123.59:1080/'  # AWS Seoul

# Замените на ваши ключи API
api_key = os.environ.get('LAGUS_BNCUS_API_KEY')
api_secret = os.environ.get('LAGUS_BNCUS_API_SECRET')

# Создание объекта для работы с биржей BinanceUS
exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'socksProxy': bncusProxy,
    })


def fetchOrderCntLastDay():
    response = exchange.privateGetRateLimitOrder()
    # print(response)
    filtered_data = [item for item in response if item['rateLimitType'] == 'ORDERS' and item['interval'] == 'DAY']
    count_value = int(filtered_data[0]['count'])
    return count_value


ordercnt=fetchOrderCntLastDay()
print(f"ordercnt sent last day: {ordercnt}")
