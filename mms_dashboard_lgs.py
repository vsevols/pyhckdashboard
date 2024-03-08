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

msymbol = 'BTC/USDC'
ssymbol = 'BTC/USDC'

masters.pop('AGRAFENIN', None)
masters.pop('STEPANOV', None)
slaves.pop('VSGMAIL', None)
slaves.pop('SMAEVSKIJ2', None)


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
        order_details = f"{order['symbol']} {order['side']} {order['price']} {order['amount']} {round(order['price']*order['amount'], 2)}"
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
    base_currency, quote_currency = msymbol.split('/')

    balance = None
    if party=="M":
        balance = exchange.fetch_balance()
    else:
        margin_iso = exchange.sapi_get_margin_isolated_account()
        # Найдем элемент с нужной валютной парой
        target_element = next(
            (asset for asset in margin_iso.get('assets', []) if
             asset.get('quoteAsset', {}).get('asset') == 'USDC' and
             asset.get('baseAsset', {}).get('asset') == 'BTC'),
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


if __name__ == "__main__":
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
        print(f"{msymbol} vs {ssymbol} rate: {common_rate} time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_balances(all_balances)


        ordercnt=fetchOrderCntLastDay(list(masters.values())[0])
        print(f"\nmasters[0] ordercnt sent last day: {ordercnt}")

        choice = input("\nPress C to exit, \"S\"ent or \"F\"illed to fetch orders, or any other key to refresh balance...").lower()

        if choice in {"s","f"}:
            break  # Прерываем цикл
        elif choice == "c":
            exit()  # Завершаем программу при выборе любой другой клавиши
        # Другие кнопки: программа повторит цикл


#===================================================================================
    if choice=="s":
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
    if choice=="f":
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

