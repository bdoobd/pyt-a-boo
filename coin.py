from binance.client import Client
import pandas as pd
from keys import api_key, secret_key

import time


def check_coin():
    client = Client(api_key, secret_key)

    """
    Получить статистические данные динамического окна 24 часового изменения стоимости.
    По всей видимости на отображение данных играет роль доступа к данным, с ключами
    тестового аккаунта выводится очень не много информации
    """
    data = client.get_ticker()
    # Конвертировать данные в табличный формат
    grid = pd.DataFrame(data)
    # Выбрать только символы в названии которых содержится строка USDT
    usdt = grid[grid.symbol.str.contains('USDT')]
    # Столбец priceChangePercent конвертировать в число с десятичными знаками
    usdt.loc[:, 'priceChangePercent'] = usdt.loc[:,
                                                 'priceChangePercent'].astype(float)
    # Отфильтровать данные с положительным значение, искрючить отрицательные
    usdt = usdt[usdt.priceChangePercent > 0]
    # Забрать только первые три столбца из таблицы для отображения данных.
    # Эти столбцы - название символа, изменение стоимости символа и
    # процентное изменение стоимости символа
    # TODO: Добавить для отображения lastPrice и volume
    # usdt = usdt.iloc[:, :3]
    usdt = usdt[['symbol', 'lastPrice', 'priceChangePercent', 'volume']]
    # Сортировка данных по столбцу priceChangePercent в порядке убывания.
    # Почему то сортировка отрицательных чисел происходит странно
    # после положительных значений как будто не учитывается знак минус и
    # сорировка опять выполняется от большего к меньшему значению.
    # Конвертируются в абсолютные числа???
    usdt = usdt.sort_values(by='priceChangePercent', ascending=False)

    pd.set_option('display.max_rows', None)
    usdt.columns = ['Монета', 'Стоимость', '% изменение', 'Объём']

    # Отображение даты и времени

    current_time = time.strftime('%H:%M:%S')

    print(f'\nЗапрос: {current_time}\n')
    print(usdt.head(20))


if __name__ == '__main__':
    # while True:
    check_coin()
    # time.sleep(5)
