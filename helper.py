# import get_symbols


# def get_lot_size(coin, list):
#     # for key in get_symbols(get_symbols.handle_json(uri)):
#     for key in list:
#         if key['symbol'] == coin:
#             for filter in key['filters']:
#                 if 'LOT_SIZE' == filter['filterType']:
#                     return filter['stepSize']


# def get_precision(string):
#     if (string.find('1')) == 0:
#         return 0

#     period = int(string.find('.'))

#     return string.find('1', period) - 1


def getAllTickers(client):
    return client.get_all_tickers()
