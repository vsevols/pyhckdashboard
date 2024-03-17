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
exchange = masters['AGRAFENIN']

# Символ торговли (например, 'FDUSD/USDT')
symbol = 'BTC/USDC'

order_ids_to_cancel = ['335780072', '335780090']

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

exit()

symbol = 'USDC/USDT'
price = 0.9996  # Замените на актуальную цену
quantity = 18  # Количество BASE для покупки

# Создайте ордер на покупку
order = exchange.create_limit_buy_order(symbol, quantity, price)

# Выведите информацию об ордере
print(order)