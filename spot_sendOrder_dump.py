import importlib

import ccxt
import os
from datetime import datetime
import sys





def set_global_variables(module):
    global masters, slaves, msymbol, ssymbol
    masters = module.masters
    slaves = module.slaves
    msymbol = module.msymbol
    ssymbol = module.ssymbol

def import_fund_module_from_arg():
    if len(sys.argv) > 1:
        module_name = sys.argv[1].replace(".py", "")

        try:
            # imported_module = __import__(module_name)
            # imported_module = sys.modules[module_name]
            imported_module = importlib.import_module(module_name)
            set_global_variables(imported_module)
        except ImportError as e:
            print(f"Не удалось импортировать модуль {module_name}: {e}")
            exit()
    else:
        print("Необходимо указать имя файла модуля в аргументах командной строки.")
        exit()

import_fund_module_from_arg()
donor = masters['AGRAFENIN']
recepient = masters['STEPANOV']
exchange = donor


asset = 'USDC'
#address = recepient.fetch_deposit_address(asset, {'network': 'BEP20'})
#print(address)

#exit()
def cancel_all_open(exchange):
    global orders
    # Получение списка активных ордеров
    symbol = 'BTC/USDC'
    orders = exchange.fetch_open_orders(symbol)
    # Отмена каждого активного ордера
    for order in orders:
        exchange.cancel_order(order['id'], symbol)


# Символ торговли (например, 'FDUSD/USDT')
symbol = 'BTC/USDC'

order_ids_to_cancel = []#['335780072', '335780090']

try:
    # Отмена ордеров по заданным ID
    for order_id in order_ids_to_cancel:
        exchange.cancel_order(order_id, symbol)
        print(f"Order {order_id} successfully cancelled.")
except ccxt.NetworkError as e:
    print(exchange.id, 'cancel_order failed due to a network error:', str(e))
except ccxt.ExchangeError as e:
    print(exchange.id, 'cancel_order failed due to exchange error:', str(e))
except Exception as e:
    print(exchange.id, 'cancel_order failed with an error:', str(e))

orders = exchange.fetch_open_orders(symbol, limit=50)
print(f"active orders {symbol}: ")
print(orders)


symbol = 'BTC/USDC'
#price = 68000  # Замените на актуальную цену
quantity = 0.00005  # Количество BASE


recepientIsSell = False


def isBaseMoreThanQuote(exchange):
    balance = exchange.fetch_balance()
    base_balance = balance.get(symbol.split('/')[0], {}).get('total', 0)
    quote_balance = balance.get(symbol.split('/')[1], {}).get('total', 0)
    ticker = exchange.fetch_ticker(symbol)
    last_price = ticker['last']
    base_equivalent = base_balance * last_price
    return base_equivalent > quote_balance

while True:
    try:
        order_book = exchange.fetch_order_book(symbol)

        depth0_bid_price = order_book['bids'][0][0] if len(order_book['bids']) > 0 else None
        depth0_ask_price = order_book['asks'][0][0] if len(order_book['asks']) > 0 else None

        recepientIsSell = isBaseMoreThanQuote(recepient)
        if recepientIsSell:
            my_bid = depth0_ask_price - 1
            print(f'{my_bid} donor buying: {my_bid}')
            recepient.create_limit_sell_order(symbol, quantity, my_bid)
            donor.create_limit_buy_order(symbol, quantity, my_bid)
        else:
            my_ask = depth0_bid_price + 1
            print(f'{my_ask} donor selling: {my_ask}')
            recepient.create_limit_buy_order(symbol, quantity, my_ask)
            donor.create_limit_sell_order(symbol, quantity, my_ask)
    except ccxt.InsufficientFunds as e:
        print("Ошибка: Недостаточно средств на счете для размещения ордера.")
        print("Подробности:", e)
        cancel_all_open(donor)
        cancel_all_open(recepient)