from binance.client import Client
from binance.exceptions import BinanceAPIException
from keys import api_key, secret_key
import json

client = Client(api_key, secret_key)

nice_print = json.dumps(client.get_account(), indent=4)

print(nice_print)
