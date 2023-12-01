# from classes.coin import Coin
import requests
import keys


class Analyze:
    def __init__(self, client) -> None:

        self.client = client

    def getAssetAveragePrice(self, symbol: str) -> float:
        try:
            return float(self.client.get_avg_price(symbol=symbol)['price'])
        except Exception as error:
            print(f'Произошла ошибка {error}')

    def getCurrentPrice(self, symbol: str) -> float:
        """Получает актуальную стоимость монеты на данный момент

        Returns:
            float: Стоимость актива
        """
        url = 'https://api.binance.com/api/v3/ticker/price'

        headers = {
            'X-MBX-APIKEY': keys.api_key
        }

        params = {
            'symbol': symbol
        }

        data = requests.get(url, params=params, headers=headers)
        ticker = data.json()

        return float(ticker['price'])
