import datetime


def getAllTickers(client):
    return client.get_all_tickers()


def printDateNow():
    return datetime.datetime.now().strftime('%H:%M:%S')
