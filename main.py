from binance.client import Client
import keys
import pandas as pd
import time
import helper
import get_symbols

# import json

coin_list = get_symbols.get_symbols()

client = Client(keys.api_key, keys.secret_key, testnet=True)

# print(client.get_account())


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
            coin, client.KLINE_INTERVAL_1MINUTE, '120')
    except:
        print('BUY cycle check error, restating after 1 minute')
        time.sleep(61)
        coin = top_coin()
        data_grid = get_last_data(
            coin, client.KLINE_INTERVAL_1MINUTE, '120')

    decimals = helper.get_precision(coin_lot_size)
    quantity = round(amount / data_grid.Close.iloc[-1], decimals)

    if (data_grid.Close.pct_change() + 1).cumprod().iloc[-1] > 1:

        print('<**** Growing Coin found ****>')
        print(f'TOP COIN: ' + str(coin))
        print(f'PRICE: ' + str(data_grid.Close.iloc[-1]))
        print(f'AVAILABLE QTY: ' + str(quantity))

        try:
            # order = client.create_test_order(
            #     symbol=coin,
            #     side=client.SIDE_BUY,
            #     type=client.ORDER_TYPE_MARKET,
            #     quantity=quantity)

            order = True

            if order:
                print('Nice shopping!')
                print(order)

            # FIXME: Не уверен, что стоимость монеты та же, что и табличке
            coin_price = data_grid.Close.iloc[-1]
            # coin_price = float(order["fills"][0]["price"])

            trade_open = True

            while trade_open:
                try:
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '2')
                except:
                    print('SELL cycle check error, restating after 1 minute')
                    time.sleep(61)
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '2')

                print('<**** SELL cycle check ****>')
                print(f'UPPER LIMIT: ' + str(coin_price * upper_limit))
                print(f'PRICE BOUGHT: ' + str(coin_price))
                print(f'GRID PRICE: ' + str(data_grid.Close[-1]))
                print(f'LOWER LIMIT: ' + str(coin_price * lower_limit))
                # print(data_grid)

                if data_grid.Close[-1] <= coin_price * lower_limit or data_grid.Close[-1] >= coin_price * upper_limit:
                    print('Time to sell coin')
                    print(data_grid.Close[-1])
                    try:
                        # order = client.create_test_order(
                        #     symbol=coin,
                        #     side=client.SIDE_SELL,
                        #     type=client.ORDER_TYPE_MARKET,
                        #     quantity=quantity
                        # )

                        # print(f'SELL oreder ready as:')
                        # print(order)

                        order = True
                    except Exception as sell_error:
                        print('Error placing SELL order')
                        print(f'Sell error: ' + str(sell_error))

                    time.sleep(5)
                    break

        except Exception as err:
            print('Error placing BUY order')
            print(f'Error:' + str(err))

    else:
        print('<=== No grows, no buy ===>')
        time.sleep(10)


while True:
    run(10)
