from classes.coin import Coin
from classes.receipt import Receipt
from classes.logger import Log
from classes.trade import Trade
import config
import time
import sys
import helper


def run(amount, position, lower_limit=0.985, upper_limit=1.02, trade_open=False):

    coin = Coin('usdt', 'test')
    # coin = Coin('usdt')

    assets = coin.mostValuable()

    chosen = assets.iloc[int(position) - 1]

    coin.setTopCoin(chosen.symbol)

    if coin.analyzeAndBuy():
        print(coin.getSymbol())
        qty = coin.getQuantity(amount=amount)

        if qty > coin.getMaxQty() or qty < coin.getMinQty():
            raise Exception(
                f'Количество {qty} для заказа не соответствует фильтру LOT_SIZE')

        trade = Trade(coin.getClient(), coin.getSymbol())

        buy_order = trade.createOrder(side='buy', qty=qty)

        if buy_order:
            receipt = Receipt()
            receipt.getBuyReceipt(buy_order)
            print(f'Выбрана и куплена монета {coin.getSymbol()}')
            print(
                f'Количество: {receipt.buyReceiptQuantity()}, стоимость {receipt.buyReceiptPrice()}')

            logger = Log(coin.getSymbol())
            logger.writeHead()
            logger.writeBuyReceipt(buy_order)

            trade_open = True

            receipt_price = receipt.buyReceiptPrice()
            receipt_qty = receipt.buyReceiptQuantity()

            previous_price = 0

            while trade_open:

                current_price = coin.currentSymbolPrice()

                up_limit = coin.setLimit(
                    price=receipt_price, percent=config.upper_limit)
                static_low_limit = coin.setLimit(
                    price=receipt_price, percent=config.lower_limit)
                dynamic_low_limit = coin.setDynamicLowLimit(
                    current_price=current_price, trade_price=receipt_price,  percent=config.lower_limit)

                print(f'{helper.printDateNow()}')
                print(f'Верхний предел торговли: {up_limit}')
                print(
                    f'Монета торгуется сейчас: {helper.colorText("green", current_price) if current_price >= previous_price else helper.colorText("red", current_price)}')
                print(
                    f'Динамический нижний предел торговли: {helper.colorText("orange", dynamic_low_limit)}')
                print(
                    f'Статический нижний предел торговли: {static_low_limit}\n')

                previous_price = current_price

                if current_price > up_limit or current_price < dynamic_low_limit:
                    sell_order = trade.createOrder(
                        side='sell', qty=receipt_qty)

                    if sell_order:
                        receipt.getSellReceipt(sell_order)
                        logger.writeSellReceipt(sell_order)

                        break
                    else:
                        raise Exception('Неудача с продажей монеты')

            sys.exit()
        else:
            raise Exception('Не удалось купить монету')

    else:
        print(
            f'>{helper.printDateNow()} <=== Монета {coin.getSymbol()} не подходит для покупки, ждёмс ===>')
        time.sleep(5)


while True:
    try:
        if len(sys.argv) < 2:
            raise ValueError('Отсутствует параметр скрипта')

        run(amount=config.trade_amount, position=sys.argv[1])
    except KeyboardInterrupt:
        print('  Обнаружено нажатие сочетания клавиш Ctrl + C, скрипт закончил работу')
        sys.exit()

    except ValueError:
        print('Укажи порядковый номер строки монеты для работы скрипта')
        sys.exit()

    except Exception as error:
        print(f'Произошла ошибка {error}')
        sys.exit()
