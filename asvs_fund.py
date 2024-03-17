import ccxt
import os

bncusProxy= 'socks5://15.164.123.59:1080/'  # AWS Seoul

# Инициализация словаря объектов ccxt.exchange для masters
masters = {
    'LAGUS': ccxt.binanceus({
        'apiKey': os.environ.get('LAGUS_BNCUS_API_KEY'),
        'secret': os.environ.get('LAGUS_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
        'options': {
            'adjustForTimeDifference': True,
        },
    }),
    'AGRAFENIN': ccxt.binanceus({
        'apiKey': os.environ.get('AGRAFENIN_BNCUS_API_KEY'),
        'secret': os.environ.get('AGRAFENIN_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
        'options': {
            'adjustForTimeDifference': True,
        },
    }),
    'STEPANOV': ccxt.binanceus({
        'apiKey': os.environ.get('STEPANOV_BNCUS_API_KEY'),
        'secret': os.environ.get('STEPANOV_BNCUS_API_SECRET'),
        'enableRateLimit': True,
        'socksProxy': bncusProxy,
        'options': {
            'adjustForTimeDifference': True,
        },
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
ssymbol = 'BTC/FDUSD'

masters.pop('LAGUS', None)
slaves.pop('LAGUSBRO', None)