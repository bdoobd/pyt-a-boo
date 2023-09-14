import os
from datetime import datetime
import json


def create_log_file_name(coin):
    logdir = f'{os.getcwd()}/logs/'
    if not (os.path.exists(logdir)):
        os.makedirs(logdir)

    if (os.path.isdir(logdir)):
        date_format = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
        log_file = f'{logdir}{date_format}_{coin}.log'

    return log_file


def write_log_header(file, coin):
    with open(file, 'a') as logfile:
        line_1 = f'========== {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} =========\n'
        line_2 = f'============== {coin} ==============\n'
        logfile.write(line_1)
        logfile.write(line_2)


def write_buy_receipt(file, data):

    with open(file, 'a') as logfile:
        logfile.write(f'Куплена монета {data["symbol"]}\n')
        if len(data['fills']) > 0:
            fills = data['fills'][0]
            logfile.write(f'Стоимость: {fills["price"]}\n')
            logfile.write(f'Количество: {fills["qty"]}\n')
        else:
            logfile.write('Пустой массив fills')


def write_cell_receipt(file, data):
    with open(file, 'a') as logfile:
        logfile.write('Продажа монеты\n')
        logfile.write(f'Тип данных CELL: {type(data)}')
        for item in data:
            logfile.write(f'Key {item} => value {data[item]}\n')

        if len(data['fills']) > 0:
            fills = data['fills'][0]
            logfile.write(f'Стоимость продажи: {fills["price"]}')
            logfile.write(f'Продано количесво: {fills["qty"]}')
        else:
            logfile.write('Опять пустой массив fills')
