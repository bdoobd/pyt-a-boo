from classes.asset import Asset
from classes.analyze import Analyze
from datetime import datetime
import pandas as pd
import json
import time


asset = Asset('usdt', 'test')
client = asset.getClient()
analyze = Analyze(client)

# pd.set_option('display.max_columns', None)


def showOpenOrders():
    orders = pd.DataFrame(client.get_open_orders())
    orders = orders.iloc[:, [0, 1, 3, 4, 5, 8, 10, 11, 14, 16]]
    orders['time'] = pd.to_datetime(orders['time'], unit='ms')
    orders['time'] = orders['time'].dt.strftime('%d.%m.%Y %H:%M:%S')
    # print(json.dumps(client.get_open_orders(), indent=4))
    return orders


def checkOrderStatus(id: int):
    print(json.dumps(client.get_order(symbol='ACAUSDT', orderId=id), indent=4))


def getTrades():
    trades = pd.DataFrame(client.get_my_trades(symbol='ACAUSDT'))
    trades = trades.iloc[:, [0, 1, 2, 4, 5, 8, 9]]
    trades['time'] = pd.to_datetime(trades['time'], unit='ms')
    trades['time'] = trades['time'].dt.strftime('%d.%m.%Y %H:%M:%S')
    print(trades)


def getAssetsNames():
    data = asset.mostValuable()

    return data['symbol'].to_list()


def tryAnalyze():
    # return analyze.getAssetAveragePrice(symbol='IRISUSDT')
    data = getAssetsNames()
    assetDic = {}
    for item in data:
        assetDic[item] = {}
        assetDic[item]['averagePrice'] = analyze.getAssetAveragePrice(
            symbol=item)
        assetDic[item]['currentPrice'] = analyze.getCurrentPrice(symbol=item)

    return assetDic


if __name__ == '__main__':
    # print(showOpenOrders())
    # checkOrderStatus(id=60837)
    # getTrades()
    start_time = time.time()
    print(getAssetsNames())
    asset_time = time.time()
    print(json.dumps(tryAnalyze(), indent=4))
    price_time = time.time()

    asset_run_time = asset_time - start_time
    price_run_time = price_time - asset_time
    full_time = price_time - start_time
    print(f'Функция полученя активов работала {asset_run_time}')
    print(
        f'Функция полученя стредней и текущей стоимости работала {price_run_time}')
    print(f'Полный цикл работы скрипта {full_time}')
