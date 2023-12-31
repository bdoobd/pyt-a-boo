from binance.client import Client
from binance.exceptions import BinanceAPIException
from keys import api_key, secret_key
from config import look_back, sell_look_back, trade_amount
import time
import sys
from top_coin import top_coin
from last_data import get_last_data
import symbol_data
# import create_logfile as log
from classes.logger import Log
import datetime

import json

client = Client(api_key, secret_key)


def run(amount, lower_limit=0.985, upper_limit=1.02, trade_open=False):

    try:
        coin = top_coin(client)
        data = client.get_historical_klines(
            coin, client.KLINE_INTERVAL_1MINUTE, look_back)
        data_grid = get_last_data(data)
    except:
        print('Ошибка процесса покупки монеты, перезапуск через одну минуту')
        time.sleep(61)
        coin = top_coin(client)
        data = client.get_historical_klines(
            coin, client.KLINE_INTERVAL_1MINUTE, look_back)
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

        logger = Log(coin)

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

                    logger.writeHead()
                    logger.writeBuyReceipt(order)

                    trade_price = float(order["fills"][0]["price"]) if len(
                        order['fills']) > 0 else coin_price
                    have_quantity = float(order['fills'][0]['qty']) if len(
                        order['fills']) > 0 else quantity

                    trade_open = True

                while trade_open:

                    try:
                        data = client.get_historical_klines(
                            coin, client.KLINE_INTERVAL_1MINUTE, sell_look_back)
                        data_grid = get_last_data(data)
                    except:
                        print(
                            'Ошибка цикла продажи монеты, перезапуск через одну минуту')
                        time.sleep(61)
                        data = client.get_historical_klines(
                            coin, client.KLINE_INTERVAL_1MINUTE, sell_look_back)
                        data_grid = get_last_data(data)

                    analyze_time = datetime.datetime.now().strftime('%H:%M:%S')

                    print(f'> ' + str(analyze_time) +
                          ' <**** Анализ роста / падения монеты ' + str(coin) + ' ****>')
                    print(f'Верхний лимит продажи: ' +
                          str(coin_price * upper_limit))
                    print(f'Стоимость покупки: ' + str(trade_price))
                    print(f'Торгуется сейчас: ' +
                          str(data_grid.Close.iloc[-1]))
                    print(f'Нижний лимит продажи: ' +
                          str(coin_price * lower_limit))

                    if data_grid.Close.iloc[-1] <= trade_price * lower_limit or data_grid.Close.iloc[-1] >= trade_price * upper_limit:
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

                            logger.writeSellReceipt(order)

                        except BinanceAPIException as err:
                            logger.writeError(err)
                        except Exception as err:
                            logger.writeError(err)

                        break

            except BinanceAPIException as err:
                logger.writeError(err)
            except Exception as err:
                logger.writeError(err)

    else:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%H:%M:%S')
        print(
            f'>{str(formatted_time)} <=== Монета {coin} не подходит для покупки, ждёмс ===>')
        time.sleep(5)


while True:
    try:
        run(trade_amount)
    except KeyboardInterrupt:
        print('  Обнаружено нажатие сочетания клавиш Ctrl + C, скрипт закончил работу')
        sys.exit()
