from binance.client import Client
from binance.exceptions import BinanceAPIException
from test_keys import api_key, secret_key
# import pandas as pd
import time
from top_coin import top_coin
from last_data import get_last_data
import symbol_data
from create_logfile import create_log_file_name, write_log_header
import datetime
import sys
# import math

import json

client = Client(api_key, secret_key, testnet=True)


def run(amount, lower_limit=0.985, upper_limit=1.02, trade_open=False):

    interval = '120'

    try:
        coin = top_coin(client)
        data = client.get_historical_klines(
            coin, client.KLINE_INTERVAL_1MINUTE, interval + 'min ago UTC')
        data_grid = get_last_data(data)
    except:
        print('Ошибка процесса покупки монеты, перезапуск через одну минуту')
        time.sleep(61)
        coin = top_coin(client)
        data = client.get_historical_klines(
            coin, client.KLINE_INTERVAL_1MINUTE, interval + 'min ago UTC')
        data_grid = get_last_data(data)

    if (data_grid.Close.pct_change() + 1).cumprod().iloc[-1] > 1:
        coin_info = client.get_symbol_ticker(symbol=coin)
        coin_price = float(coin_info['price'])

        symbol_exchange_data = client.get_symbol_info(coin)

        precision = symbol_data.get_precision(symbol_exchange_data)

        quantity = round(amount / coin_price, precision)

        print('<**** Найдена растущая монета ****>')
        print(f'Тип монеты: ' + str(coin))
        print(f'Стоимость: ' + str(data_grid.Close.iloc[-1]))
        print(f'Request price: ' + str(coin_price))
        print(f'Количество для покупки: ' + str(quantity))

        symbol_info = client.get_symbol_info(coin)
        symbol_json = json.dumps(symbol_info, indent=4)

        with open('symbol.json', 'w') as output:
            output.write(symbol_json)

        log_file_name = create_log_file_name(coin)
        write_log_header(log_file_name, coin)

        if quantity < symbol_data.get_minQty(symbol_exchange_data) or quantity > symbol_data.get_maxQty(symbol_exchange_data):
            print('Объём заказа не соответствует фильтру')
        else:
            print('Операция удволетворяет фильтру LOT_SIZE')
            try:
                order = client.create_order(
                    symbol=coin,
                    side=client.SIDE_BUY,
                    type=client.ORDER_TYPE_MARKET,
                    quantity=quantity)

                if order:
                    print(f'<**** Удачная покупка, куплена монета ' +
                          str(coin) + ' ****>')

                    nice_order = json.dumps(order, indent=4)

                    with open('BUY_order_receipt.json', 'w') as buy_receipt:
                        buy_receipt.write(nice_order)
                # FIXME: В квитке может быть пустой массив fills[], получить стоимость и количесво оттуда не получится
                trade_price = float(order["fills"][0]["price"])
                have_quantity = float(order['fills'][0]['qty'])

                trade_open = True

                while trade_open:
                    interval = '2'

                    try:
                        data = client.get_historical_klines(
                            coin, client.KLINE_INTERVAL_1MINUTE, interval + 'min ago UTC')
                        data_grid = get_last_data(data)
                    except:
                        print(
                            'Ошибка цикла продажи монеты, перезапуск через одну минуту')
                        time.sleep(61)
                        data = client.get_historical_klines(
                            coin, client.KLINE_INTERVAL_1MINUTE, interval + 'min ago UTC')
                        data_grid = get_last_data(data)

                    analyze_time = datetime.datetime.now().strftime('%H:%M:%S')

                    print(f'> ' + str(analyze_time) +
                          ' <**** Анализ роста / падения монеты ' + str(coin) + ' ****>')
                    print(f'Верхний лимит продажи: ' +
                          str(coin_price * upper_limit))
                    print(f'Стоимость покупки: ' + str(coin_price))
                    print(f'Торгуется сейчас: ' + str(data_grid.Close[-1]))
                    print(f'Нижний лимит продажи: ' +
                          str(coin_price * lower_limit))

                    if data_grid.Close[-1] <= trade_price * lower_limit or data_grid.Close[-1] >= trade_price * upper_limit:
                        print('<**** Время продавать монету ****>')
                        print(f'Количество для продажи ' +
                              str(have_quantity) + ' шт')

                        try:
                            order = client.create_order(
                                symbol=coin,
                                side=client.SIDE_SELL,
                                type=client.ORDER_TYPE_MARKET,
                                quantity=have_quantity
                            )

                            print('<**** Монета продана со следующими данными ****')
                            nice_sell_order = json.dumps(order, indent=4)
                            # FIXME: Квиток может содержать несколько элементов массива fills[] с разными стоимостями и количеством
                            with open('SELL_order_receipt.json', 'w') as sell_order:
                                sell_order.write(nice_sell_order)

                        except BinanceAPIException as err:
                            print('Ошибка заказа на продажу монеты')
                            print(f'Статус код: ' + str(err.status_code))
                            print(f'Ответ: ' + str(err.response))
                            print(f'Код ошибки : ' + str(err.code))
                            print(f'Описание: ' + str(err.message))
                            print(f'Запрос: ' + str(err.request))

                        break

            except BinanceAPIException as err:
                print('Ошибка заказа покупки монеты')
                print(f'Статус код: ' + str(err.status_code))
                print(f'Ответ: ' + str(err.response))
                print(f'Код ошибки : ' + str(err.code))
                print(f'Описание: ' + str(err.message))
                print(f'Запрос: ' + str(err.request))

    else:
        current_time = datetime.datetime.now()
        formated_time = current_time.strftime('%H:%M:%S')
        print(
            f'>{str(formated_time)} <=== Монета {coin} не подходит для покупки, ждёмс ===>')
        time.sleep(5)


while True:
    run(15)
