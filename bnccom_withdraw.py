import ccxt
import os


api_key = os.environ.get('STEPANOV_BNCUS_API_KEY')
api_secret = os.environ.get('STEPANOV_BNCUS_API_SECRET')



# Создайте объект Binance с использованием ключей API

exchange = ccxt.binance({

    'apiKey': api_key,

    'secret': api_secret,
    'socksProxy': 'socks5://15.164.123.59:1080/',

})

#print(api_key)

balances = exchange.fetch_balance()
print(balances)

exit()



# Установите адрес кошелька BEP20 (Binance Smart Chain) на который вы хотите вывести средства

withdrawal_address = '0xb8ba53e5bd5a0482c01c0f2cedc7a71f55923643'



# Укажите токен, который вы хотите вывести

symbol = 'USDT'  # Замените на нужный токен



# Укажите сумму для вывода

amount = 42.84  # Замените на нужную сумму



# Опции вывода

params = {

    'network': 'BSC',  # Укажите сеть (Binance Smart Chain)

    'addressTag': '',  # Опциональный тэг адреса, если необходим

}



# Выполните вывод средств

response = exchange.withdraw(symbol, amount, withdrawal_address, params=params)



# Выведите результат

print(response)

