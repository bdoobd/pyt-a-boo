import requests
import json

uri = 'https://api.binance.com/api/v3/exchangeInfo'


def handle_json(api_url):
    response = requests.get(api_url)
    data = response.text

    return data


def get_symbols():

    serialized = json.loads(handle_json(uri))

    return serialized['symbols']
