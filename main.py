from binance.client import Client
from binance.exceptions import BinanceAPIException
import test_keys
import pandas as pd
import time
# import helper
# import get_symbols
import datetime
import sys
import math

import json

# coin_list = get_symbols.get_symbols()

client = Client(test_keys.api_key, test_keys.secret_key, testnet=True)

"""
Функция поиска монеты USDT которая показывает максимальный рост на момент запуска функции

return string Название монетеы
"""


def top_coin():
    # Выбрать все тикеры для всех монет
    all_tickers = pd.DataFrame(client.get_ticker())
    # Отфильтровать тикеры в названиях которых есть USDT
    usdt = all_tickers[all_tickers.symbol.str.contains("USDT")]
    # Отфильтровать тикеры, удалить строки в названии которых есть строки UP и DOWN
    work = usdt[
        ~((usdt.symbol.str.contains("UP")) | (usdt.symbol.str.contains("DOWN")))
    ]
    # Выбрать строку из фрейма в котором столбец priceChangePercent имеет максимальное значение
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    # Из отфильтрованной строки выбрать первую колонку с названием монеты
    top_coin = top_coin.symbol.values[0]

    return top_coin


def get_last_data(symbol, period, interval):
    # Получить исторические данные для монеты за заданный период
    data = pd.DataFrame(client.get_historical_klines(
        symbol, period, interval + 'min ago UTC'))
    # Выбрать все строки и столбцы с первого по шестой (индекс с 0 по 5)
    data = data.iloc[:, :6]
    # Задать заголовки этим столбцам
    data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # Проиндексировать столбец Time, типа столбца для сортировки
    data = data.set_index('Time')
    # Конвертирует дату в милисекундах в обычное отображение даты
    data.index = pd.to_datetime(data.index, unit='ms')
    # Конвертирует содержимое ячеек таблицы в число с плавающей точкой
    data = data.astype('float')

    return data


# Степень точности указания стосмости монеты
# coin_lot_size = helper.get_lot_size(top_coin(), coin_list)x
# symbol_info = client.get_symbol_info(top_coin())
# coin_price = client.get_symbol_ticker(symbol=top_coin())

# print(json.dumps(symbol_info, indent=4))
# print(json.dumps(coin_price, indent=4))


def run(amount, lower_limit=0.985, upper_limit=1.02, trade_open=False):
    try:
        coin = top_coin()
        data_grid = get_last_data(
            coin, client.KLINE_INTERVAL_1MINUTE, '120')
    except:
        print('Ошибка процесса покупки монеты, перезапуск через одну минуту')
        time.sleep(61)
        coin = top_coin()
        data_grid = get_last_data(
            coin, client.KLINE_INTERVAL_1MINUTE, '120')

    # decimals = helper.get_precision(coin_lot_size)

    coin_info = client.get_symbol_ticker(symbol=top_coin())
    coin_price = float(coin_info['price'])

    # print(json.dumps(coin_info, indent=4))
    # sys.exit()
    # qty = amount / float(coin_price['price'])

    # print(f'Количество для покупкиЮ ' + str(qty))
    # print(json.dumps(symbol_info['filters'], indent=4))

    for filter in symbol_info['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            step_size = float(filter['stepSize'])
            min_qty = float(filter['minQty'])
            max_qty = float(filter['maxQty'])
            break

    precision = int(round((-math.log(step_size, 10)), 0))
    # print(step_size)
    # print(precision)

    quantity = round(amount / coin_price, precision)
    # TODO: Придумать как прикрутить проверку этого условия
    if quantity < min_qty or quantity > max_qty:
        print('Объём заказа соответствует фильтру')

    # print(f'Реальное количество для покупки: ' + str(quantity))

    # quantity = round(amount / data_grid.Close.iloc[-1], decimals)

    if (data_grid.Close.pct_change() + 1).cumprod().iloc[-1] > 1:

        symbol_info = client.get_symbol_info(coin)
        symbol_json = json.dumps(symbol_info, indent=4)

        with open('symbol.json', 'w') as output:
            output.write(symbol_json)

        print('<**** Найдена растущая монета ****>')
        print(f'Тип монеты: ' + str(coin))
        print(f'Стоимость: ' + str(data_grid.Close.iloc[-1]))
        print(f'Количество для покупки: ' + str(quantity))

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

                with open('BUY_order_receipt.py', 'w') as buy_receipt:
                    buy_receipt.write(nice_order)
                # print(nice_order)

            trade_price = float(order["fills"][0]["price"])
            have_quantity = float(order['fills'][0]['qty'])

            trade_open = True

            while trade_open:
                try:
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '2')
                except:
                    print('Ошибка цикла продажи монеты, перезапуск через одну минуту')
                    time.sleep(61)
                    data_grid = get_last_data(
                        coin, client.KLINE_INTERVAL_1MINUTE, '2')

                analyze_time = datetime.datetime.now().strftime('%H:%M:%S')

                print(f'> ' + str(analyze_time) +
                      ' <**** Анализ роста / падения монеты ' + str(coin) + ' ****>')
                print(f'Верхний лимит продажи: ' +
                      str(coin_price * upper_limit))
                print(f'Стоимость покупки: ' + str(coin_price))
                print(f'Торгуется сейчас: ' + str(data_grid.Close[-1]))
                print(f'Нижний лимит продажи: ' +
                      str(coin_price * lower_limit))
                # print(data_grid)

                if data_grid.Close[-1] <= trade_price * lower_limit or data_grid.Close[-1] >= trade_price * upper_limit:
                    print('<**** Время продавать монету ****>')
                    print(f'Количество для продажи ' +
                          str(have_quantity) + ' шт')
                    # print(data_grid.Close[-1])
                    try:
                        order = client.create_order(
                            symbol=coin,
                            side=client.SIDE_SELL,
                            type=client.ORDER_TYPE_MARKET,
                            quantity=have_quantity
                            # quantity=quantity
                        )

                        print('<**** Монета продана со следующими данными ****')
                        nice_sell_order = json.dumps(order, indent=4)

                        with open('SELL_order_receipt.py', 'w') as sell_order:
                            sell_order.write(nice_sell_order)
                        # print(nice_sell_order)
                    except BinanceAPIException as err:
                        print('Ошибка заказа на продажу монеты')
                        print(f'Статус код: ' + str(err.status_code))
                        print(f'Ответ: ' + str(err.response))
                        print(f'Код ошибки : ' + str(err.code))
                        print(f'Описание: ' + str(err.message))
                        print(f'Запрос: ' + str(err.request))

                    # time.sleep(5)
                    # TODO: После выявления всех ошибок раскоментировать break
                    # break
                    sys.exit(999000)

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
        print(f'> ' + str(formated_time) +
              ' <=== Не найден ни один актуальный вариант, ждёмс ===>')
        time.sleep(5)


while True:
    run(15)
