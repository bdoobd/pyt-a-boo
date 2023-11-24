import keys
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import config
import time
import math

import requests
import datetime
import helper


class Coin:

    def __init__(self, pair='', type='main'):
        if type.lower() == 'test':
            self.client = Client(
                keys.api_key_test, keys.secret_key_test, testnet=True)
        else:
            self.client = Client(keys.api_key, keys.secret_key)

        self.pair = pair.upper()
        self.top_coin = None
        self.asset_info = None
        self.max = 0

    def getClient(self):
        """Получить объект клиента

        Returns:
            _type_: объект клиента
        """
        return self.client

    def getTicker(self):
        """Получить 24 часовую статистику по тороговой ситуации с монетами
           При использовании фильтра при создании объекта, статистика выводится только по отфильтрованым монетам

           Данные отсортированы по полю процентного изменения стоимости монеты в порядке убывания

        Raises:
            ValueError: _description_

        Returns:
            _type_: pandas.core.frame.DataFrame
        """
        tickers = pd.DataFrame(self.client.get_ticker())

        if self.pair == '':
            filtered = tickers
        else:
            filtered = tickers[tickers.symbol.str.contains(self.pair)]
            filtered = filtered[~((filtered.symbol.str.contains("UP")) | (
                filtered.symbol.str.contains("DOWN")))]

        columns = filtered.filter(
            items=['symbol', 'priceChange', 'priceChangePercent', 'openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'volume', 'quoteVolume'])

        columns.loc[:, 'priceChangePercent'] = columns.loc[:,
                                                           'priceChangePercent'].astype(float)

        columns = columns[columns.priceChangePercent > 0]
        columns = columns.sort_values(by='priceChangePercent', ascending=False)

        if len(columns.index) == 0:
            raise ValueError('Ничего на найдено')

        return columns

    def mostValuable(self, qty=config.row_qty):
        """Получить n:ное количество строк пар с наибольшим процентуальным ростом

        Args:
            qty (_type_, optional): Количество строк. Defaults to row_qty.

        Returns:
            _type_: DataFrame
        """
        return self.getTicker().head(qty)

    def setTopCoin(self, symbol) -> None:
        """Установить монету в объекте

        Args:
            symbol (_type_): Обозначение монеты
        """
        self.top_coin = symbol
        self.asset_info = self.getSymbolInfo()

    def getSymbolInfo(self):
        return self.client.get_symbol_info(self.top_coin)

    def symbolInfo(self):
        """Получить инфрмацию о монете с помощью ExchangeInfo endpoint

        Returns:
            Dict: Торговые данные по монете включая фильтры
        """
        return self.asset_info

    def getKLine(self, period):
        """Получить исторические данные торгов по заданной паре за определённый период с частотой в одну минуту

        Args:
            period (_type_): Период, данные за который надо получить

        Returns:
            _type_: DataFrame с историческими данными
        """
        data = pd.DataFrame(self.client.get_historical_klines(
            self.top_coin, self.client.KLINE_INTERVAL_1MINUTE, period))
        data = data.iloc[:, :6]

        data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']

        data = data.set_index('Time')

        data.index = pd.to_datetime(data.index, unit='ms')

        # data = data.sort_values(by='Close', ascending=False)
        data = data.astype(float)

        pd.set_option('display.max_columns', None)

        return data

    def getStepSize(self):
        for filter in self.asset_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                return float(filter['stepSize'])

    def getTickSize(self):
        for filter in self.asset_info['filters']:
            if filter['filterType'] == 'PRICE_FILTER':
                return float(filter['tickSize'])

    def getFilteredPrice(self, amount):
        precision = int(round(-math.log(self.getTickSize(), 10), 0))

        return round(float(amount), precision)

    def getQuantity(self, amount):
        precision = int(round(-math.log(self.getStepSize(), 10), 0))

        # return round(amount / self.getAssetPrice()[1], precision)
        return round(amount / self.currentSymbolPrice(), precision)

    def getMaxQty(self):
        for filter in self.asset_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                return float(filter['maxQty'])

    def getMinQty(self):
        for filter in self.asset_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                return float(filter['minQty'])

    def getSellQuantity(self, amount):
        precision = int(round(-math.log(self.getTickSize(), 10), 0))
        return round(amount, precision)

    def getSymbol(self) -> str:
        """Получить название символьной пары (монеты)

        Returns:
            str: Строка с названием монеты
        """
        return self.top_coin

    def getMaxPrice(self) -> float:
        """Получить максимальную стомиость торгующейся монеты

        Returns:
            float: Максимальная стоимость за период торговли
        """
        return float(self.max)

    def setLimit(self, price, percent) -> float:
        """Устанавливает лимит торговали при котором монета продаётся

        Args:
            price (float): Стоимость покупки монеты 
            percent (float): Дробное число для расчёта процета для лимита, число более 1 - положительный процент, число менее 1 и более 0 - отрицательный процент

        Returns:
            float: Лимит торговли
        """
        limit = price * percent

        return float(limit)

    def setDynamicLowLimit(self, current_price, trade_price, percent) -> float:
        """Устанавливает динамический нижний лимит торговли который увиличивается при росте монеты, но не падате при падении стоимости монеты

        Args:
            current_price (float): Стоимость актива на момент вызова метода
            trade_price (float): Стоимость покупки актива
            percent (float): Процент для расчёта лимита

        Returns:
            float: Динамическая лимитная стоимость
        """
        if self.max == 0:
            self.max = trade_price

        if current_price > self.max:
            self.max = current_price

        dynamic_limit = self.max * percent

        return float(dynamic_limit)

    def analyzeAndBuy(self) -> bool:
        """Проанализировать историческую ситуацию с торговлей указанной монеты и вынести решение о покупке

        Returns:
            bool: При не балгоприятной обстановке возвращается ЛОЖЬ, в обратном случае - ПРАВДА
        """
        try:
            data_grid = self.getKLine(config.look_back)
        except:
            print(
                f'Ошибка получения исторических данных символа {self.top_coin} для покупки')
            print('Следующая попытка через минуту ...')
            time.sleep(60)
            data_grid = self.getKLine(config.look_back)

        done = (data_grid.Close.pct_change() + 1).cumprod().iloc[-1]

        return True if done > 1 else False

    def currentSymbolPrice(self) -> float:
        """Получает актуальную стоимость монеты на данный момент

        Returns:
            float: Стоимость актива
        """
        url = 'https://api.binance.com/api/v3/ticker/price'

        headers = {
            'X-MBX-APIKEY': keys.api_key
        }

        params = {
            'symbol': self.getSymbol()
        }

        data = requests.get(url, params=params, headers=headers)
        ticker = data.json()

        return float(ticker['price'])

    # def createOrder(self, side, quantity):
    #     operation = self.client.SIDE_BUY if side == 'buy' else self.client.SIDE_SELL
    #     try:
    #         order = self.client.create_order(
    #             symbol=self.top_coin,
    #             side=operation,
    #             type=self.client.ORDER_TYPE_MARKET,
    #             quantity=quantity
    #         )

    #         self.buy_receipt = order
    #     except BinanceAPIException as error:
    #         print(f'Произошла ошибка покупки {self.top_coin}\n')
    #         print(f'Статус код: {error.status_code}\n')
    #         print(f'Ответ: {error.response}\n')
    #         print(f'Код ошибки: {error.code}\n')
    #         print(f'Описание: {error.message}\n')
    #         print(f'Запрос: {error.request}\n')
    #     except Exception as err:
    #         print(f'Произошла ошибка {err}')
    #     else:
    #         return order
