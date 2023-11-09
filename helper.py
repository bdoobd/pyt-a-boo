import datetime

colors = {
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'BLUE': '\033[34m',
    'RESET': '\033[0m',
    'ORANGE': '\033[33m',
    'PURPLE': '\033[35m',
    'CYAN': '\033[36m',
}


def getAllTickers(client):
    return client.get_all_tickers()


def printDateNow():
    return datetime.datetime.now().strftime('%H:%M:%S')


def colorText(color: str, text: str) -> str:
    return '{0}{1}{2}'.format(colors[color.upper()], text, colors['RESET'])
