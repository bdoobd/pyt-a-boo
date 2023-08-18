from binance.client import Client
import keys
import pandas as pd
import time
import helper
import get_symbols

# import json

coin_list = get_symbols.get_symbols()

client = Client(keys.api_key, keys.secret_key, testnet=True)


def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains("USDT")]
    work = usdt[
        ~((usdt.symbol.str.contains("UP")) | (usdt.symbol.str.contains("DOWN")))
    ]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]

    return top_coin


def get_last_data(symbol, period, interval):
    data = pd.DataFrame(client.get_historical_klines(
        symbol, period, interval + 'min ago UTC'))
    data = data.iloc[:, :6]
    data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    data = data.set_index('Time')
    data.index = pd.to_datetime(data.index, unit='ms')
    data = data.astype('float')

    return data


coin_lot_size = helper.get_lot_size(top_coin(), coin_list)


def run(amount, lower_limit=0.985, upper_limit=1.02, trade_open=False):
    try:
        coin = top_coin()
        data_grid = get_last_data(
            top_coin(), client.KLINE_INTERVAL_1MINUTE, '120')
    except:
        print('BUY cycle check error, restating after 1 minute')
        time.sleep(61)
        coin = top_coin()
        data_grid = get_last_data(
            top_coin(), client.KLINE_INTERVAL_1MINUTE, '120')

    decimals = helper.get_precision(coin_lot_size)
    quantity = round(amount / data_grid.Close.iloc[-1], decimals)

    print('<**** Looking for BUY process ****>')
    print(f'TOP COIN: ' + str(coin))
    print(f'PRICE: ' + str(data_grid.Close.iloc[-1]))
    print(f'AVAILABLE QTY: ' + str(quantity))

    if (data_grid.Close.pct_change() + 1).cumprod().iloc[-1] > 1:
        try:
            order = client.create_test_order(
                symbol=coin,
                side=client.SIDE_BUY,
                type=client.ORDER_TYPE_MARKET,
                quantity=quantity)

            if order:
                print('Nice shopping!')
                print(order)

            # FIXME: Не уверен, что стоимость монеты та же, что и табличке
            # coin_price = data_grid.Close.iloc[-1]
            coin_price = float(order["fills"][0]["price"])

            trade_open = True

            while (trade_open):
                try:
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '120')
                except:
                    print('SELL cycle check error, restating after 1 minute')
                    time.sleep(61)
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '120')

                upper_threshold = coin_price * upper_limit
                lower_threshold = coin_price * lower_limit
                print('<**** SELL cycle check ****>')
                print(f'PRICE BOUGHT: ' + str(coin_price))
                print(f'UPPER LIMIT: ' + str(upper_threshold))
                print(f'LOWER LIMIT: ' + str(lower_threshold))

                if coin_price <= lower_threshold or coin_price >= upper_limit:
                    print('Time to sell coin')
                    try:
                        order = client.create_test_order(
                            symbol=coin,
                            side=client.SIDE_SELL,
                            type=client.ORDER_TYPE_MARKET,
                            quantity=quantity
                        )
                    except:
                        print('Error placing SELL order')

                    break

        except:
            print('Error placing BUY order')

    else:
        print('<=== No grows, no buy ===>')
        time.sleep(10)


while True:
    run(10)
