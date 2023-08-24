import pandas as pd


def get_last_data(data):

    data = pd.DataFrame(data)
    # Выбрать все строки и столбцы с первого по шестой (индекс с 0 по 5)
    data = data.iloc[:, :6]
    # Задать заголовки этим столбцам
    data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # Проиндексировать столбец Time, типа столбца для сортировки
    data = data.set_index('Time')
    # Конвертирует дату в милисекундах в обычное отображение даты
    data.index = pd.to_datetime(data.index, unit='ms')
    # Конвертирует содержимое ячеек таблицы в число с плавающей точкой
    data = data.astype('float')

    return data
