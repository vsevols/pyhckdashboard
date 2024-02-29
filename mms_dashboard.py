﻿import ccxt
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

bncusProxy= 'socks5://15.164.123.59:1080/'  # Замените на ваши параметры SOCKS5 прокси

# Инициализация словаря объектов ccxt.exchange для masters
masters = {
    'LAGUS': ccxt.binanceus({
        'apiKey': os.environ.get('LAGUS_BNCUS_API_KEY'),
        'secret': os.environ.get('LAGUS_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
    }),
    'AGRAFENIN': ccxt.binanceus({
        'apiKey': os.environ.get('AGRAFENIN_BNCUS_API_KEY'),
        'secret': os.environ.get('AGRAFENIN_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
    }),
    'STEPANOV': ccxt.binanceus({
        'apiKey': os.environ.get('STEPANOV_BNCUS_API_KEY'),
        'secret': os.environ.get('STEPANOV_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
    }),
}

# Инициализация словаря объектов ccxt.exchange для slaves
slaves = {
    'LAGUSBRO': ccxt.binance({
        'apiKey': os.environ.get('LAGUSBRO_BNCCOM_API_KEY'),
        'secret': os.environ.get('LAGUSBRO_BNCCOM_API_SECRET'),
    }),
    'VSGMAIL': ccxt.binance({
        'apiKey': os.environ.get('VSGMAIL_BNCCOM_API_KEY'),
        'secret': os.environ.get('VSGMAIL_BNCCOM_API_SECRET'),
    }),
    'SMAEVSKIJ2': ccxt.binance({
        'apiKey': os.environ.get('SMAEVSKIJ2_BNCCOM_API_KEY'),
        'secret': os.environ.get('SMAEVSKIJ2_BNCCOM_API_SECRET'),
    }),
}

def fetch_orders(args):
    exchange, symbol = args
    # Получаем отправленные ордера по торговой паре
    orders = exchange.fetch_orders(symbol, limit=10)
    return orders

def fetch_filled_orders(args):
    exchange, symbol = args
    # Получаем все заполненные ордера по торговой паре
    filled_orders = exchange.fetch_closed_orders(symbol)
    return [{'account_name': exchange.id, 'type': 'MASTER' if exchange in masters.values() else 'SLAVE', **order} for order in filled_orders]


def print_orders(title, orders):
    print(f"\n{title}:\n{'Date':<20}{'Account Name':<20}{'Order Details':<50}")
    for order in orders:
        date = datetime.fromtimestamp(order['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        account_name = order['account_name']
        order_details = f"{order['symbol']} {order['type']} {order['side']} {order['price']} {order['amount']}"
        print(f"{date:<20}{account_name:<20}{order_details:<50}")

def print_orders_combo(title, orders):
    print(f"\n{title}:\n{'Date':<20}{'Account Name':<20}{'Order Type':<10}{'Order Details':<50}")
    for order in orders:
        date = datetime.fromtimestamp(order['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        account_name = order['account_name']
        order_type = order['type']
        order_details = f"{order['symbol']} {order['side']} {order['price']} {order['amount']}"
        print(f"{date:<20}{account_name:<20}{order_type:<10}{order_details:<50}")

if __name__ == "__main__":
    msymbol = 'BTC/USDC'
    ssymbol = 'BNB/USDC'

#===================================================================================
    all_orders = []
    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        orders_lists = executor.map(fetch_orders, zip(masters.values(), [msymbol]*len(masters)))
        for account_name, orders in zip(masters.keys(), orders_lists):
            all_orders.extend([{'account_name': account_name, **order} for order in orders])
	
    # Сортировка объединенного списка по дате
    all_orders_sorted = sorted(all_orders, key=lambda x: x['timestamp'])
	
    print_orders("Master orders", all_orders_sorted)

#===================================================================================

    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        master_orders_lists = executor.map(fetch_filled_orders, [(exchange, msymbol) for exchange in masters.values()])
        slave_orders_lists = executor.map(fetch_filled_orders, [(exchange, ssymbol) for exchange in slaves.values()])

        for account_name, master_orders in zip(masters.keys(), master_orders_lists):
            all_orders.extend(master_orders)

        for account_name, slave_orders in zip(slaves.keys(), slave_orders_lists):
            all_orders.extend(slave_orders)

    # Сортировка объединенного списка по дате
    all_orders_sorted = sorted(all_orders, key=lambda x: x['timestamp'])

    # Вывод информации
    print_orders_combo("Filled Orders", all_orders_sorted)