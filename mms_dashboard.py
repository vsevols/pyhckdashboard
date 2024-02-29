import ccxt
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

bncusProxy= 'socks5://15.164.123.59:1080/'  # AWS Seoul

# Инициализация словаря объектов ccxt.exchange для masters
masters = {
    'LAGUS': ccxt.binanceus({
        'apiKey': os.environ.get('LAGUS_BNCUS_API_KEY'),
        'secret': os.environ.get('LAGUS_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy
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
        'socksProxy': bncusProxy,
    }),
}

#for acc_name, exchange in slaves.items():
#    print(f"checking access: {acc_name}")
#    orders = exchange.fetch_open_orders(symbol="BTC/USDT")


def fetch_orders(args):
    exchange, symbol = args
    # Получаем отправленные ордера по торговой паре
    orders = exchange.fetch_orders(symbol, limit=10)
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
    filled_orders = exchange.fetch_my_trades(symbol) #.fetch_closed_orders(symbol)
    party=None
    if exchange in masters.values():
        party="M"
    if exchange in slaves.values():
        party="S"

    return [{'account_name': get_account_name(exchange), 'party': party, **order} for order in filled_orders]


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
        party = order['party']
        order_details = f"{order['symbol']} {order['side']} {order['price']} {order['amount']}"
        print(f"{date:<20}{account_name:<20}{party:<10}{order_details:<50}")

def get_balance(args):
    exchange, symbol=args
    account_name = get_account_name(exchange)

    # Получаем баланс для указанного символа
    balance = exchange.fetch_balance()
    base_currency, quote_currency = msymbol.split('/')

    quote_amount = balance['total'][quote_currency]
    base_amount = balance['total'][base_currency]
    rate = 1  # !!!!!!!!!!!!!!!!! Предполагаем, что курс базовой валюты равен 1
    return {'account_name': account_name, 'party': getParty(exchange), 'quote_amount': quote_amount, 'base_amount': base_amount, 'rate': rate}

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

    total_iq = 0

    # Вывод балансов
    for balance in balances:
        print(f"{balance['account_name']:<{column_widths['account_name']}}{balance['party']:<{column_widths['party']}}{balance['quote_amount']:<{column_widths['quote_amount']}}{balance['base_amount']:<{column_widths['base_amount']}}{balance['base_amount']*balance['rate']:<{column_widths['baseAmount*rate']}}{balance['quote_amount']+balance['base_amount']*balance['rate']:<{column_widths['quoteAmount+baseAmount*rate']}}")
        total_iq += balance['quote_amount']+balance['base_amount']*balance['rate']


    print(f"\nTotal IQ: {total_iq}")



if __name__ == "__main__":
    msymbol = 'BTC/USDC'
    ssymbol = 'BNB/USDC'
    while True:

        all_balances = []
        with ThreadPoolExecutor() as executor:
            # Используем executor.map для распараллеливания обращений к биржам
            master_balances = executor.map(get_balance, zip(masters.values(), [msymbol]*len(masters)))
            slave_balances = executor.map(get_balance, zip(slaves.values(), [ssymbol]*len(slaves)))

            all_balances.extend([balance for balance in master_balances if balance])
            all_balances.extend([balance for balance in slave_balances if balance])

        common_rate = list(slaves.values())[0].fetch_ticker(ssymbol)['bid']
        for balance in all_balances:
            balance['rate'] = common_rate

        # Распечатаем все балансы
        print(f"{msymbol} vs {ssymbol} rate: {common_rate}")
        print_balances(all_balances)

        choice = input("\nPress B to refresh balance, O to fetch orders, or any other key to exit...").lower()

        if choice == "o":
            break  # Прерываем цикл, если выбран "O"
        elif choice != "b":
            exit()  # Завершаем программу при выборе любой другой клавиши
        # Если выбрано "B", то программа повторит цикл


#===================================================================================
    all_orders = []
    with ThreadPoolExecutor() as executor:
        # Используем executor.map для распараллеливания обращений к биржам
        orders_lists = executor.map(fetch_orders, zip(masters.values(), [msymbol]*len(masters)))
        for account_name, orders in zip(masters.keys(), orders_lists):
            all_orders.extend([{'account_name': account_name, **order} for order in orders])
	
    # Сортировка объединенного списка по дате
    all_orders_sorted = sorted(all_orders, key=lambda x: x['timestamp'])
#TODO: обрезать список здесь	
    print_orders("Master sent orders", all_orders_sorted)

#===================================================================================

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

