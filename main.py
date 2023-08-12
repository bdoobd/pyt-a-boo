from binance.client import Client
import keys
import pandas as pd
import time
import requests
import json

uri = 'https://api.binance.com/api/v3/exchangeInfo'


def handle_json(api_url):
    #   coin = 'ASTRUSDT'
    response = requests.get(api_url)
    data = response.text

    return data


def get_symbols(raw_data):

    serialized = json.loads(raw_data)

    return serialized['symbols']


print(get_symbols(handle_json(uri)))


# print(handle_json(uri))

# formatted = json.dumps(response, indent=2)
# formatted = json.loads(data)

# output = json.dumps(formatted)

# print(formatted['symbols'][]['symbol'])
# print(type(formatted))

# for key in formatted['symbols']:
# output = ''
# if 'USDT' in key['symbol']:
#     output = key['symbol']
#     for filter in key['filters']:
#         if 'LOT_SIZE' in (filter['filterType']):
# output = output + ' LOT_SIZE is ' + filter['stepSize']
# print(filter['stepSize'])
# print(output)
