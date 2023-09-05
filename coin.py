from binance.client import Client
import pandas as pd
from test_keys import api_key, secret_key
# import json
import time


def check_coin():
    client = Client(api_key, secret_key, testnet=True)

    data = client.get_all_tickers()
    """
    Данные вывода get_all_tickers()
    """
    # data = data['symbol']
    # print(json.dumps(data, indent=4))
    # for item in data:
    #     if 'USDT' in item['symbol']:
    #         print(item['symbol'])
    """
    Данные вывода get_ticker()
    """
    """
    Получить статистические данные динамического окна 24 часового изменения стоимости.
    По всей видимости на отображение данных играет роль доступа к данным, с ключами
    тестового аккаунта выводится очень не много информации
    """
    data = client.get_ticker()
    # Конвертировать данные в табличный формат
    grid = pd.DataFrame(data)
    # Выбрать только символы в названии которых содержится строка USDT
    grid = grid[grid.symbol.str.contains('USDT')]
    # Забрать только первые три столбца из таблицы для отображения данных.
    # Эти столбцы - название символа, изменение стоимости символа и
    # процентное изменение стоимости символа
    grid = grid.iloc[:, :3]
    # Сортировка данных по столбцу priceChangePercent в порядке убывания.
    # Почему то сортировка отрицательных чисел происходит странно
    # после положительных значений как будто не учитывается знак минус и
    # сорировка опять выполняется от большего к меньшему значению.
    # Конвертируются в абсолютные числа???
    grid = grid.sort_values(by='priceChangePercent', ascending=False)

    print(grid)


if __name__ == '__main__':
    while True:
        check_coin()
        time.sleep(5)
