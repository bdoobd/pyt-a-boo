from binance.client import Client
import keys
import pandas as pd
import time
import helper
import get_symbols

coin_list = get_symbols.get_symbols()

client = Client(keys.api_key, keys.secret_key)


def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains("USDT")]
    work = usdt[
        ~((usdt.symbol.str.contains("UP")) | (usdt.symbol.str.contains("DOWN")))
    ]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]

    return top_coin


coin_lot_size = helper.get_lot_size(top_coin(), coin_list)

print(f'COIN: ' + str(top_coin()) + ' with precision ' +
      str(coin_lot_size))

print(helper.get_precision(coin_lot_size))
