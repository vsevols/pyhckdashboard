import importlib
import sys

import ccxt
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

masters = slaves = msymbol = ssymbol = None



#for acc_name, exchange in slaves.items():
#    print(f"checking access: {acc_name}")
#    orders = exchange.fetch_open_orders(symbol="BTC/USDT")


def fetch_orders(args):
    exchange, symbol = args
    # Получаем отправленные ордера по торговой паре
    party=getParty(exchange)
    orders = None
    if party=="M":
        orders = exchange.fetch_orders(symbol, limit=50)
    else:
        orders = exchange.fetch_orders(symbol, None, 50, {'marginMode': 'isolated'})

    return orders

def fetch_open_orders(args):
    exchange, symbol = args
    # Получаем активные ордера по торговой паре
    party=getParty(exchange)
    orders = None
    if party=="M":
        orders = exchange.fetch_open_orders(symbol, limit=50)
    else:
        orders = exchange.fetch_open_orders(symbol, None, 50, {'marginMode': 'isolated'})

    return orders

def get_account_name(exchange):
    for key, val in masters.items():
        if val == exchange:
            return key
    for key, val in slaves.items():
        if val == exchange:
            return key
    return None

def getParty(exchange):
    for key, val in masters.items():
        if val == exchange:
            return 'M';
    for key, val in slaves.items():
        if val == exchange:
            return 'S';
    return None


def fetch_filled_orders(args):
    exchange, symbol = args
    # Получаем все заполненные ордера по торговой паре
    party=getParty(exchange)
    filled_orders = None
    if party=="M":
        filled_orders = exchange.fetch_my_trades(symbol) #.fetch_closed_orders(symbol)
    else:
        filled_orders = exchange.fetch_my_trades(symbol, None, 50, {'marginMode': 'isolated'})

    return [{'account_name': get_account_name(exchange), 'party': party, **order} for order in filled_orders]


def print_orders(title, orders):
    print(f"\n{title}:\n{'Date':<20}{'Account Name':<20}{'Order Details':<50}")
    for order in orders:
        date = datetime.fromtimestamp(order['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        account_name = order['account_name']
        order_details = f"{order['symbol']} {order['side']} {order['price']} {order['amount']} {round(order['price']*order['amount'], 2)} {order['clientOrderId']}"
        print(f"{date:<20} {account_name:<15}{order_details:<50}")

def print_orders_combo(title, orders):
    print(f"\n{title}:\n{'Date':<20}{'Account Name':<20}{'Order Type':<10}{'Order Details':<50}")
    for order in orders:
        date = datetime.fromtimestamp(order['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        account_name = order['account_name']
        party = order['party']
        order_details = f"{order['symbol']} {order['side']} {order['price']} {order['amount']} {round(order['price']*order['amount'], 2)}"
        print(f"{date:<20} {account_name:<15}{party:<2}{order_details:<50}")

def get_balance(args):
    exchange, symbol=args
    account_name = get_account_name(exchange)

    party=getParty(exchange)
    base_currency = quote_currency = None

    balance = None
    if party=="M":
        balance = exchange.fetch_balance()
        base_currency, quote_currency = msymbol.split('/')
    else:
        base_currency, quote_currency = ssymbol.split('/')
        margin_iso = exchange.sapi_get_margin_isolated_account()
        # Найдем элемент с нужной валютной парой
        target_element = next(
            (asset for asset in margin_iso.get('assets', []) if
             asset.get('quoteAsset', {}).get('asset') == quote_currency and
             asset.get('baseAsset', {}).get('asset') == base_currency),
            None
        )
        if target_element is None:
            return {
                    'account_name': account_name,  # Замените на ваш аккаунт
                    'party': 'S',  # Замените на ваш тип (M или S)
                    'quote_amount': 0.,
                    'base_amount': 0.
                   }
            

        return {
                'account_name': account_name,  # Замените на ваш аккаунт
                'party': 'S',  # Замените на ваш тип (M или S)
                'quote_amount': float(target_element['quoteAsset']['netAsset']),
                'base_amount': float(target_element['baseAsset']['netAsset'])
               }
        

    quote_amount = balance['total'][quote_currency]
    base_amount = balance['total'][base_currency]
    return {'account_name': account_name, 'party': getParty(exchange), 'quote_amount': quote_amount, 'base_amount': base_amount}

def print_balances(balances):
    # Определение ширины каждого столбца
    column_widths = {
        'account_name': 15,
        'party': 5,
        'quote_amount': 15,
        'base_amount': 15,
        'baseAmount*rate': 15,
        'quoteAmount+baseAmount*rate': 25
    }

    # Вывод заголовка
    print(f"{'Account Name':<{column_widths['account_name']}}{'pty':<{column_widths['party']}}{'Quote':<{column_widths['quote_amount']}}{'Base':<{column_widths['base_amount']}}{'BaseIQ':<{column_widths['baseAmount*rate']}}{'Total IQ':<{column_widths['quoteAmount+baseAmount*rate']}}")

    total_quote_amount = 0
    total_base_amount = 0
    total_base_amount_rate = 0
    total_iq = 0

    # Вывод балансов
    for balance in all_balances:
        account_name = balance['account_name']
        party = balance['party']
        quote_amount = balance['quote_amount']
        base_amount = balance['base_amount']
        base_amount_rate = round(base_amount * balance['rate'], 2)
        total_value = quote_amount + base_amount_rate

        print(f"{account_name:<{column_widths['account_name']}}{party:<{column_widths['party']}}{quote_amount:<{column_widths['quote_amount']}}{base_amount:<{column_widths['base_amount']}}{base_amount_rate:<{column_widths['baseAmount*rate']}} {total_value:<{column_widths['quoteAmount+baseAmount*rate']}}")        
        total_quote_amount += quote_amount
        total_base_amount += base_amount
        total_base_amount_rate += base_amount_rate
        total_iq += total_value
        
    dummy="*"
    account_name="_TOTAL_"
    print(f"{account_name:<{column_widths['account_name']}}{dummy:<{column_widths['party']}}{round(total_quote_amount, 2):<{column_widths['quote_amount']}}{total_base_amount:<{column_widths['base_amount']}} {round(total_base_amount_rate,2):<{column_widths['baseAmount*rate']}} {total_iq:<{column_widths['quoteAmount+baseAmount*rate']}}")        


def fetchOrderCntLastDay(exchange):
    response = exchange.privateGetRateLimitOrder()
    # print(response)
    filtered_data = [item for item in response if item['rateLimitType'] == 'ORDERS' and item['interval'] == 'DAY']
    count_value = int(filtered_data[0]['count'])
    return count_value


def show_balances():
    global all_balances, executor
    all_balances = []
    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        master_balances = executor.map(get_balance, zip(masters.values(), [msymbol] * len(masters)))
        slave_balances = executor.map(get_balance, zip(slaves.values(), [ssymbol] * len(slaves)))

        all_balances.extend([balance for balance in master_balances if balance])
        all_balances.extend([balance for balance in slave_balances if balance])
    common_rate = list(slaves.values())[0].fetch_ticker(ssymbol)['bid']
    for balance in all_balances:
        balance['rate'] = common_rate
    # Распечатаем все балансы
    print(f"{msymbol} vs {ssymbol} rate: {common_rate} time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_balances(all_balances)
    for master_id, master_data in masters.items():
        ordercnt = fetchOrderCntLastDay(master_data)
        print(f"masters[{master_id}] ordercnt sent last day: {ordercnt}")


def show_sent_orders():
    global all_orders, executor, orders_lists, account_name, orders, all_orders_sorted
    all_orders = []
    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        orders_lists = executor.map(fetch_orders, zip(masters.values(), [msymbol] * len(masters)))
        for account_name, orders in zip(masters.keys(), orders_lists):
            all_orders.extend([{'account_name': account_name, **order} for order in orders])
    # Сортировка объединенного списка по дате
    all_orders_sorted = sorted(all_orders, key=lambda x: x['timestamp'])
    # TODO: обрезать список здесь
    print_orders("Master sent orders", all_orders_sorted)


def show_active_orders():
    global all_orders, executor, orders_lists, account_name, orders, all_orders_sorted
    all_orders = []
    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        orders_lists = executor.map(fetch_open_orders, zip(masters.values(), [msymbol] * len(masters)))
        for account_name, orders in zip(masters.keys(), orders_lists):
            all_orders.extend([{'account_name': account_name, **order} for order in orders])
    # Сортировка объединенного списка по дате
    all_orders_sorted = sorted(all_orders, key=lambda x: x['timestamp'])
    # TODO: обрезать список здесь
    print_orders("Master active orders", all_orders_sorted)


def show_filled_orders():
    global all_orders, executor, account_name, all_orders_sorted
    all_orders = []
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
    print_orders_combo("ALL Filled Orders", all_orders_sorted)


def action_selected(choice):
    if choice == "b":
        while True:
            try:
                show_balances()
                break
            except Exception as e:
                print(f"{e}, retrying...")
                continue
    # ===================================================================================
    if choice == "s":
        while True:
            try:
                show_sent_orders()
                break
            except Exception as e:
                print(f"{e}, retrying...")
                continue
    # ===================================================================================
    if choice == "a":
        while True:
            try:
                show_active_orders()
                break
            except Exception as e:
                print(f"{e}, retrying...")
                continue
    # ===================================================================================
    if choice == "f":
        while True:
            try:
                show_filled_orders()
                break
            except Exception as e:
                print(f"{e}, retrying...")
                continue

def set_global_variables(module):
    global masters, slaves, msymbol, ssymbol
    masters = module.masters
    slaves = module.slaves
    msymbol = module.msymbol
    ssymbol = module.ssymbol



if __name__ == "__main__":
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

    choice="b"
    while True:
        action_selected(choice)

        prevChoice = choice
        choice = input("\nPress C to exit, \"B\"alance, \"S\"ent or \"F\"illed or \"A\"ctive to fetch orders, or Enter to refresh...").lower()
        if choice == "":
            choice = prevChoice

        if choice == "c":
            exit()



