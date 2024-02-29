import ccxt
import os
from datetime import datetime
import sys

# Замените на ваши ключи API
api_key = os.environ.get('LAGUS_BNCUS_API_KEY')
api_secret = os.environ.get('LAGUS_BNCUS_API_SECRET')

# Создание объекта для работы с биржей BinanceUS
exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,  # Управление частотой запросов
    'socksProxy': 'socks5://15.164.123.59:1080/'  # Замените на ваши параметры SOCKS5 прокси
})


symbol = 'BTC/USDC'

def print_orders(orders, title):
    print(f"\n{title} ({symbol}):\n")
    for order in orders:
        timestamp = datetime.fromtimestamp(order['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        maker_or_taker = order.get('takerOrMaker')
        #maker_or_taker = "Maker" if is_maker else "Taker" if is_maker is not None else ""
        if maker_or_taker is None:
             maker_or_taker=""
        else:
            maker_or_taker="- " + maker_or_taker

        print(f"{timestamp} - {order['side']} - {order['price']} - {order['amount']} - {order['price'] * order['amount']} {maker_or_taker}")
    #print(f"Order Data: {order}")



# Получение последних исполненных ордеров
try:
    executed_orders = exchange.fetch_my_trades(symbol=symbol, limit=500)
    print_orders(executed_orders, "Последние N исполненных ордеров")

except ccxt.NetworkError as e:
    print(f'Ошибка сети: {e}')
except ccxt.ExchangeError as e:
    print(f'Ошибка биржи: {e}')
except Exception as e:
    print(f'Неизвестная ошибка: {e}')

# Получение всех активных ордеров
try:
    active_orders = exchange.fetch_open_orders(symbol=symbol)
    print_orders(active_orders, "Активные ордеры")

    if len(sys.argv) == 2 and sys.argv[1] == '-cancel':
        # Отмена всех активных ордеров
        for order in active_orders:
            order_id = order['id']
            response = exchange.cancel_order(id=order_id, symbol=symbol)
            print(f"Отменен ордер: {order_id}, Статус: {response['status']}")


except ccxt.NetworkError as e:
    print(f'Ошибка сети: {e}')
except ccxt.ExchangeError as e:
    print(f'Ошибка биржи: {e}')
except Exception as e:
    print(f'Неизвестная ошибка: {e}')

# Получение последних N отправленных ордеров
try:
    all_orders = exchange.fetch_orders(symbol=symbol, limit=60)
    #canceled_orders = [order for order in all_orders if order['status'] == 'canceled']
    print_orders(all_orders, "Последние N отправленных ордеров")


except ccxt.NetworkError as e:
    print(f'Ошибка сети: {e}')
except ccxt.ExchangeError as e:
    print(f'Ошибка биржи: {e}')
except Exception as e:
    print(f'Неизвестная ошибка: {e}')


# Получение информации об аккаунте (баланс)
try:
    account_info = exchange.fetch_balance()
    balances = account_info['total']

    for asset, balance in balances.items():
        if balance != 0 :
            print(f'{asset}: {balance}')

except ccxt.NetworkError as e:
    print(f'Ошибка сети: {e}')
except ccxt.ExchangeError as e:
    print(f'Ошибка биржи: {e}')
except Exception as e:
    print(f'Неизвестная ошибка: {e}')