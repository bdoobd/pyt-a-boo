from classes.asset import Asset
from classes.receipt import Receipt
from classes.logger import Log
from classes.trade import Trade
import config
import time
import sys
import helper


def run(amount, trade_open=False):

    asset = Asset(type='test')

    # TODO: Получить имя актива от пользователя
    user_asset = input('Укажи имя актива для работы: ').upper()

    # TODO: Проверить есть ли на бирже соответствующий актив, если нет, выбросить исключение

    print(user_asset)

    while user_asset not in asset.getAssetNames():
        user_asset = input(
            f'Двнный актив {user_asset} не найен. Укажи новое имя актива для работы: ').upper()

    asset.setTopCoin(user_asset)
    # coin.setTopCoin(user_asset)

    # Работаем с активом
    print(f'Выбран актив {asset.getSymbol()}')
    print(f'Торгуется сейчас: {asset.currentSymbolPrice()}')
    print(f'Средняя стоимость: {asset.getAveragePrice()["price"]}')

    choice = input('Выбрать этот актив для работы? Y / N: ').upper()

    if choice == 'Y':
        # print(coin.getSymbol())
        qty = asset.getQuantity(amount=amount)

        if qty > asset.getMaxQty() or qty < asset.getMinQty():
            raise Exception(
                f'Количество {qty} для заказа не соответствует фильтру LOT_SIZE')

        trade = Trade(asset.getClient(), asset.getSymbol())

        buy_order = trade.createOrder(side='buy', qty=qty)

        if buy_order:
            receipt = Receipt()
            receipt.getBuyReceipt(buy_order)
            print(f'Выбрана и куплена монета {asset.getSymbol()}')
            print(
                f'Количество: {receipt.buyReceiptQuantity()}, стоимость {receipt.buyReceiptPrice()}')

            logger = Log(asset.getSymbol())
            logger.writeHead()
            logger.writeBuyReceipt(buy_order)

            trade_open = True

            receipt_price = receipt.buyReceiptPrice()
            receipt_qty = receipt.buyReceiptQuantity()

            previous_price = 0

            while trade_open:

                current_price = asset.currentSymbolPrice()

                up_limit = asset.setLimit(
                    price=receipt_price, percent=config.upper_limit)
                static_low_limit = asset.setLimit(
                    price=receipt_price, percent=config.lower_limit)
                dynamic_low_limit = asset.setDynamicLowLimit(
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

                        print(
                            f'Монета была куплена: {receipt.buyReceiptPrice()}')
                        print(f'Монета продана: {receipt.sellReceptPrice()}')
                        print(
                            f'Разница: {receipt.buyReceiptPrice() - receipt.sellReceptPrice()}\n')

                        break
                    else:
                        raise Exception('Неудача с продажей монеты')

            sys.exit()
        else:
            raise Exception('Не удалось купить монету')

    else:
        # print(
        #     f'>{helper.printDateNow()} <=== Монета {coin.getSymbol()} не подходит для покупки, ждёмс ===>')
        # time.sleep(1)
        print('Переадресация на новый выбор актива -> ')


while True:
    try:
        # if len(sys.argv) < 2:
        #     raise ValueError('Отсутствует параметр скрипта')

        run(amount=config.trade_amount)
    except KeyboardInterrupt:
        print('  Обнаружено нажатие сочетания клавиш Ctrl + C, скрипт закончил работу')
        sys.exit()

    except ValueError:
        print('Укажи порядковый номер строки монеты для работы скрипта')
        sys.exit()

    except Exception as error:
        print(f'Произошла ошибка {error}')
        sys.exit()
