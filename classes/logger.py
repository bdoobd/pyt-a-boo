from pathlib import Path
from datetime import datetime

import json


class Log:

    def __init__(self, coin) -> None:
        self.coin = coin
        self.logDirectory = self.checkLogDir(Path.cwd() / 'logfiles')

        self.logFile = self.logDirectory / self.createLogFile()

    # def getCoin(self):
    #     print(self.coin)

    # def getLogDir(self):
    #     print(self.logDirectory)

    # def getLogFile(self):
    #     print(self.logFile)

    def checkLogDir(self, path):
        if not path.exists():
            try:
                path.mkdir()
            except:
                print('Не могу создать папку для логов')

        return path

    def createLogFile(self):
        date_format = datetime.now().strftime('%Y_%m_%d-%H-%M-%S')
        filename = f'{date_format}_{self.coin}.log'

        return filename

    def writeHead(self):
        with open(self.logFile, 'a', encoding='UTF-8') as log:
            log.write(
                f'========== {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} =====\n')
            log.write(f'============== {self.coin} ==============\n')

    def writeBuyReceipt(self, data):
        with open(self.logFile, 'a', encoding='UTF-8') as log:
            log.write(f'======== Квиток покупки ========\n')
            log.write(f'Куплена монета: {data["symbol"]} *********\n')
            if len(data['fills']) > 0:
                for row in data['fills']:
                    log.write(f'Куплено количество: {row["qty"]}\n')
                    log.write(f'Стоимость покупки: {row["price"]}\n')
            else:
                log.write('Массив fills[] пустой\n')

            log.write(f'{json.dumps(data, indent=4)}\n')

    def writeSellReceipt(self, data):
        with open(self.logFile, 'a', encoding='UTF-8') as log:
            log.write(f'======== Квиток продажи ========\n')
            log.write(f'Монета {data["symbol"]} продана ***********\n')
            if len(data['fills']) > 0:
                for row in data['fills']:
                    log.write(f'Продано количество: {row["qty"]}\n')
                    log.write(f'Стоимость продажи: {row["price"]}\n')
            else:
                log.write('Массив fills[] пустой')

            log.write(f'{json.dumps(data, indent=4)}\n')

    def writeError(self, error):
        with open(self.logFile, 'a', encoding='UTF-8') as log:
            log.write('Произошла ошибка!!!\n')
            # log.write(f'Статус код: {error.status_code}\n')
            # log.write(f'Ответ: {error.response}\n')
            # log.write(f'Код ошибки: {error.code}\n')
            # log.write(f'Описание: {error.message}\n')
            # log.write(f'Запрос: {error.request}\n')
            log.write(str(error))
