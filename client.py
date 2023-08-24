from binance.client import Client
from binance.exceptions import BinanceAPIException
import test_keys
import json

import helper

client = Client(test_keys.api_key, test_keys.secret_key, testnet=True)

nice_print = json.dumps(client.get_account(), indent=4)

# print(nice_print)

print(helper.getAllTickers(client))
