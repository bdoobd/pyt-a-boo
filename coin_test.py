from classes.coin import Coin
import matplotlib.pyplot as plt
import helper
import time
import config
import sys


def trackCoin():
    trade_start = False
    # 1. Получить символ монеты с максимальным ростом за прошедшие 24 часа
    # coin = Coin('usdt', 'test')
    coin = Coin('usdt')

    # =============================================================================

    # print(coin.getTicker())
    # sys.exit()

    # Тест выбора пары
    assets = coin.mostValuable(20)
    print(assets)

    row = int(input('Выбери строку для анализа данных '))

    chosen = assets.iloc[row - 1]

    coin.setTopCoin(chosen.symbol)

    prevPrice = 0

    print(coin.currentSymbolPrice())
    # sys.exit()

    # print(type(coin.currentSymbolPrice(coin.getSymbol())))

    # while True:
    #     try:
    #         currentPrice = coin.currentSymbolPrice()

    #         # red_string = f'{helper.RED}{currentPrice}{helper.RESET}'
    #         red_string = f'{helper.RED}{currentPrice}{helper.RESET}'
    #         # green_string = f'{helper.GREEN}{currentPrice}{helper.RESET}'
    #         green_string = f'{helper.GREEN}{currentPrice}{helper.RESET}'
    #         print(
    #             f'{helper.printDateNow()} - {coin.getSymbol()} стоимость {green_string if currentPrice >= prevPrice else red_string}')
    #         tickerPrice = coin.currentSymbolPrice()
    #         # print(
    #         #     f'Symbol {tickerPrice["symbol"]} price {tickerPrice["price"]}')
    #         prevPrice = currentPrice
    #         # time.sleep(5)
    #     except KeyboardInterrupt:
    #         print('Вход из скрипта... ')
    #         break

    # sys.exit()
    # =============================================================================

    # 2. Проверить происходит ли рост монеты за определённый период и вынести решение о её покупке
    if coin.analyzeAndBuy():
        # 3. После решения о покупке создать BUY заказ
        print(f'{helper.printDateNow()}. Place buy order {coin.getSymbol()}')
        # print(dir(coin))
        # 4. При удачном завершении заказа записать данные покупки в свойство класса. Наверное лучше создать класс Trade или даже BuyTrade
        # TODO: Записать квиток покупки в свойсво класса coin.success_buy_order
        # print(
        # f'\nКуплена монета {coin.getSymbol()}, стоимость {coin.getSymbolPrice()}')
        buy_price = coin.currentSymbolPrice()

        trade_start = True

        while trade_start:
            # 5. Проверять состояние торговли монетой с установкой минимального и максимального лимита
            # - Взять стоимость покупки из заказа
            upper_limit = coin.setLimit(buy_price, config.upper_limit)
            lower_limit = coin.setLimit(buy_price, config.lower_limit)
            trade_price = coin.currentSymbolPrice()
            dynamic_low_limit = coin.setDynamicLowLimit(
                current_price=trade_price, trade_price=buy_price, percent=config.lower_limit)
            # buy_price = coin.getSymbolPrice()

            print(
                f'\nКуплена монтеа {coin.getSymbol()}, стоимость {buy_price}')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(f'Верхний порог >>>>>>>>>>>>>>>>>>>>> {upper_limit}')
            print(
                f'Торгуется сейчас {coin.getSymbol()}, стоимость {trade_price}')
            print(f'Нижний порог >>>>>>>>>>>>>>>>>>>>> {lower_limit}')
            print(f'Динамический порог >>>>>>>>>>>>>>> {dynamic_low_limit}')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    #         print(f'Максимальная стоимость >>>>>>>>>>> {max_price}\n')

            # 6. При достижении какого то лимита создать CELL заказ
            if trade_price > upper_limit or trade_price < lower_limit:
                print('Монета достигла лимита, продана')

                # 7. При удачном завершении заказа записать данные в свойство класса

                # 8. Создать заказ на обмен пары на USDT используя данные из квитка о продаже монеты
                break

            time.sleep(5)

    else:
        print(f'{helper.printDateNow()} Не найдена монета для покупки')


if __name__ == '__main__':

    while True:
        trackCoin()
        time.sleep(3)
