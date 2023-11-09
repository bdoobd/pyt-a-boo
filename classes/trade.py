from binance.exceptions import BinanceAPIException


class Trade:

    def __init__(self, client, asset) -> None:
        self.client = client
        self.asset = asset

    def createOrder(self, side: str, qty: float) -> None:
        trade_type = self.client.SIDE_BUY if side.upper() == 'BUY' else self.client.SIDE_SELL

        try:
            order = self.client.create_order(
                symbol=self.asset,
                side=trade_type,
                type=self.client.ORDER_TYPE_MARKET,
                quantity=qty
            )

            self.buy_receipt = order
        except BinanceAPIException as error:
            print(f'Произошла ошибка покупки {self.asset}\n')
            print(f'Статус код: {error.status_code}\n')
            print(f'Ответ: {error.response}\n')
            print(f'Код ошибки: {error.code}\n')
            print(f'Описание: {error.message}\n')
            print(f'Запрос: {error.request}\n')
        except Exception as err:
            print(f'Произошла ошибка {err}')
        else:
            return order
