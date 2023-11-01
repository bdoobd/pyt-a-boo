import keys
from binance.client import Client
import pandas as pd
from config import look_back, sell_look_back, trade_amount
import time


class Coin:

    def __init__(self, pair=''):
        self.client = Client(keys.api_key, keys.secret_key)
        self.pair = pair.upper()
        # self.getTopCoin()
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
            return tickers

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

        # return columns.head(20)
        return columns

    def mostValuable(self, qty=20):
        # TODO: Добавить обработку количества заданных строк:
        #     - число
        #     - в диапазоне функции getTicker()
        return self.getTicker().head(qty)

    def setTopCoin(self, symbol) -> None:
        self.top_coin = symbol

    def getTopCoin(self) -> None:
        """Получить символ монеты и её стоимость Last Price из данных 24 часовой статистики

        Returns:
            None:
            list: [0] - символ монеты, [1] - стоимость (float)
        """
        coin_data = self.getTicker()

        coin = coin_data.iloc[0]

        self.top_coin = coin['symbol']
        self.top_coin_price = float(coin['lastPrice'])

        return coin_data
# ============================================================

    def getAssetPrice(self) -> list:
        """Запрос актуальной торгующейся на этот момент стоимости монеты

        Returns:
            list: Массив [0] - название пары, [1] - стоимость пары
        """
        data = pd.DataFrame(self.client.get_all_tickers())

        asset = data.query(f'symbol == @self.top_coin')

        list = asset.values.tolist()

        return [list[0][0], float(list[0][1])]
# ============================================================

    def getSymbolPrice(self) -> float:
        """Получить стоимость монеты из объекта

        Returns:
            float: Стоимость монеты
        """
        return self.top_coin_price
# ============================================================

    def getSymbol(self) -> str:
        """Получить название символьной пары (монеты)

        Returns:
            str: Строка с названием монеты
        """
        return self.top_coin
# ============================================================

    def getMaxPrice(self) -> float:
        """Получить максимальную стомиость торгующейся монеты

        Returns:
            float: Максимальная стоимость за период торговли
        """
        return self.max
# ============================================================

    def setUpLimit(self, up=1.02):

        upper_limit = self.top_coin_price * up

        if self.top_coin_price < float(self.getAssetPrice()[1]):
            upper_limit = float(self.getAssetPrice()[1]) * up

        return upper_limit
# ============================================================

    def setLowLimit(self, low=0.99):
        lower_limit = self.top_coin_price * low
        # TODO: Для отслеживания порога продажи надо попробовать создать свойство MAX и ТОРГОВАЯ СТОИМОСТЬ в классе и проверять что из них больше, чтобы держать максимальную стоимость известной. Потом можно прикрутить нижний порог к максимальной стоимости для меньших протерь при падении монеты
        self.tradePrice = float(self.getAssetPrice()[1])
        if self.tradePrice > self.max:
            self.max = self.tradePrice

        dynamic_limit = self.max * low

        return [lower_limit, dynamic_limit]
# ============================================================

    def getKLine(self):
        data = pd.DataFrame(self.client.get_historical_klines(
            self.top_coin, self.client.KLINE_INTERVAL_1MINUTE, look_back))
        data = data.iloc[:, :6]

        data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']

        data = data.set_index('Time')

        data.index = pd.to_datetime(data.index, unit='ms')

        # data = data.sort_values(by='Close', ascending=False)
        data = data.astype(float)

        pd.set_option('display.max_columns', None)

        return data
# ============================================================

    def getKLinePrice(self):

        data = self.getKLine()

        return data.loc[:, 'Close'].iloc[-1]
# ============================================================

    def analyzeAndBuy(self) -> bool:
        try:
            data_grid = self.getKLine()
        except:
            print(
                f'Ошибка получения исторических данных символа {self.top_coin}')
            print('Следующая попытка через минуту ...')
            time.sleep(60)
            data_grid = self.getKLine()

        # pct = data_grid.iloc[:, 3]

        # tmp = data_grid.Close

        # pct = data_grid.Close.tolist()
        # # tmp['Pct'] = pct
        # data_grid['Pct'] = pct
        # data_grid.Pct.pct_change()
        # # return data_grid.Close.pct_change()

        # data_grid = data_grid.loc[:, ['Close', 'Pct']]
        # data_grid = data_grid.Pct.pct_change()
        # data_grid['Pct'] = data_grid['Pct'].apply(lambda x: x.pct_change())

        # return (data_grid.Pct.pct_change() + 1).cumprod()

        # done = (data_grid.Pct.pct_change() + 1).cumprod().iloc[-1]
        done = (data_grid.Close.pct_change() + 1).cumprod().iloc[-1]

        return True if done > 1 else False

    def getOrderBookTicker(self, symbol=''):
        params = {'symbol': symbol}
        return self.client.get_orderbook_ticker(symbol=symbol)
