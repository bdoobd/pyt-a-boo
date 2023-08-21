from binance.client import Client
from binance.exceptions import BinanceAPIException
import test_keys
import pandas as pd
import time
import helper
import get_symbols
import datetime

import json

coin_list = get_symbols.get_symbols()

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


symbol_info = client.get_symbol_info(top_coin())
symbol_json = json.dumps(symbol_info, indent=4)


with open('symbol.json', 'w') as output:
    output.write(symbol_json)


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
coin_lot_size = helper.get_lot_size(top_coin(), coin_list)


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

    decimals = helper.get_precision(coin_lot_size)
    quantity = round(amount / data_grid.Close.iloc[-1], decimals)

    # FIXME: При попытке купить монеты выскакивала ошибка фильтра, выделенных средств было меньше, чем минимально разрешённая покупка. Данные о монете находятся в client.get_symbol_info(symbol)

    if (data_grid.Close.pct_change() + 1).cumprod().iloc[-1] > 1:

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
                print('<**** Удачная покупка ****>')
                nice_order = json.dumps(order, indent=4)
                print(nice_order)

            coin_price = float(order["fills"][0]["price"])
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

                print('<**** Анализ роста / падения монеты ****>')
                print(f'Верхний лимит продажи: ' +
                      str(coin_price * upper_limit))
                print(f'Стоимость покупки: ' + str(coin_price))
                print(f'Торгуется сейчас: ' + str(data_grid.Close[-1]))
                print(f'Нижний лимит продажи: ' +
                      str(coin_price * lower_limit))
                # print(data_grid)

                if data_grid.Close[-1] <= coin_price * lower_limit or data_grid.Close[-1] >= coin_price * upper_limit:
                    print('<**** Время продавать монету ****>')
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
                        print(nice_sell_order)
                    except BinanceAPIException as err:
                        print('Ошибка заказа на продажу монеты')
                        print(f'Код ошибки: ' + str(err.status_code))
                        print(f'Описание: ' + str(err.message))

                    time.sleep(5)
                    break

        except BinanceAPIException as err:
            print('Ошибка заказа покупки монеты')
            print(f'Код ошибки: ' + str(err.status_code))
            print(f'Описание: ' + str(err.message))

    else:
        current_time = datetime.datetime.now()
        formated_time = current_time.strftime('%H:%M:%S')
        print(f'> ' + str(formated_time) +
              ' <=== Не найден ни один актуальный вариант, ждёмс ===>')
        time.sleep(5)


while True:
    run(15)
