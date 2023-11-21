from classes.coin import Coin


class Asset(Coin):
    def __init__(self, pair='', type='main'):
        super().__init__(pair, type)
        self.asset_names = self.setAssetNames()

    def setAssetNames(self) -> list:
        names = []

        for asset in self.client.get_all_tickers():
            names.append(asset['symbol'])

        return names

    def getAssetNames(self) -> list:
        return self.asset_names

    def getAveragePrice(self) -> dict:
        return self.client.get_avg_price(symbol=self.getSymbol())
