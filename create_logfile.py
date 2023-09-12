import os
from datetime import datetime


def create_log_file_name(coin):
    logdir = f'{os.getcwd()}/logs/'

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
