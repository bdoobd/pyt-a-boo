import pandas as pd

"""
Функция поиска монеты USDT которая показывает максимальный рост на момент запуска функции

return string Название монетеы
"""


def top_coin(client):
    # Выбрать все тикеры для всех монет
    all_tickers = pd.DataFrame(client.get_ticker())
    # Отфильтровать тикеры в названиях которых есть USDT
    usdt = all_tickers[all_tickers.symbol.str.contains("USDT")]
    # Отфильтровать тикеры, удалить строки в названии которых есть строки UP и DOWN
    work = usdt[
        ~((usdt.symbol.str.contains("UP")) | (usdt.symbol.str.contains("DOWN")))
    ]
    # Выбрать строку из фрейма в котором столбец priceChangePercent имеет максимальное значение
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    # Из отфильтрованной строки выбрать первую колонку с названием монеты
    top_coin = top_coin.symbol.values[0]

    return top_coin
