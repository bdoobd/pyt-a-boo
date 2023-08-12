# from binance.client import Client
# import keys
# import pandas as pd
# import time
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


# formatted_string = json.dumps(get_symbols(handle_json(uri)), indent=2)
# print(type(formatted_string))


for key in get_symbols(handle_json(uri)):
    # TODO:  Нужен coin в названии которого есть USDT
    if 'USDT' in key['symbol']:
        # TODO: В symbol есть ключ filter который содержит массив фильтров
        for filter in key['filters']:
            # TODO: Нужный тип фильтра LOT_SIZE
            if 'LOT_SIZE' in filter['filterType']:
                print(str(key['symbol']) + ' => ' + json.dumps(filter))
            # print(filter['filterType'])
            # TODO: Нашёл почему дублиуются coins, кроме фильтра LOT_SIZE есть фильтр MARKET_LOT_SIZE. Как сделать более строгий выбор фильтра? Что то типа filterType === 'LOT_SIZE'.
