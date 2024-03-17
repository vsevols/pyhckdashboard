import ccxt
import os

api_key = os.environ.get('AGRAFENIN_BNCUS_API_KEY')
api_secret = os.environ.get('AGRAFENIN_BNCUS_API_SECRET')

# Создайте объект Binance с использованием ключей API
exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': api_secret,
    'socksProxy': 'socks5://15.164.123.59:1080/',
})

#print(api_key)

#account_info = exchange.fetch_balance()
#balances = account_info
#print(balances)

# Установите адрес кошелька BEP20 (Binance Smart Chain) на который вы хотите вывести средства
withdrawal_address = '0xb8ba53e5bd5a0482c01c0f2cedc7a71f55923643'

# Укажите токен, который вы хотите вывести
symbol = 'USDC'  # Замените на нужный токен

# Укажите сумму для вывода
amount = 30.4  # Замените на нужную сумму

# Опции вывода
params = {
    'network': 'BSC',  # Укажите сеть (Binance Smart Chain)
    'addressTag': '',  # Опциональный тэг адреса, если необходим
}

# Выполните вывод средств
response = exchange.withdraw(symbol, amount, withdrawal_address, params=params)

# Выведите результат
print(response)
