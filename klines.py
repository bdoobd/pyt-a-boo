from binance.client import Client
from binance.exceptions import BinanceAPIException
from keys import api_key, secret_key
from top_coin import top_coin
import pandas as pd

from last_data import get_last_data

client = Client(api_key, secret_key)


def data_grid():
    coin = top_coin(client)
    coin_data = client.get_historical_klines(
        coin, client.KLINE_INTERVAL_1MINUTE, '60min ago UTC')
    coin_grid = pd.DataFrame(coin_data)
    coin_grid = coin_grid.iloc[:, :6]
    coin_grid.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    coin_grid = coin_grid.set_index('Time')
    coin_grid.index = pd.to_datetime(coin_grid.index, unit='ms')
    # coin_grid['Time'] = pd.to_datetime(coin_grid['Time'], unit='ms')
    coin_grid = coin_grid.astype('float')
    # coin_grid.loc[:, 'Close'] = coin_grid.loc[:, 'Close'].pct_change() + 1
    # coin_grid.loc[:, 'Close'] = coin_grid.loc[:, 'Close'].cumprod()

    print(coin_grid)
    # print(get_last_data(coin_data))


if __name__ == '__main__':
    data_grid()
