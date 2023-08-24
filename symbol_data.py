import math


def get_stepSize(data):
    for filter in data['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            return float(filter['stepSize'])
            # step_size = float(filter['stepSize'])
            # min_qty = float(filter['minQty'])
            # max_qty = float(filter['maxQty'])
            # break


def get_minQty(data):
    for filter in data['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            # step_size = float(filter['stepSize'])
            # min_qty = float(filter['minQty'])
            return float(filter['minQty'])
            # max_qty = float(filter['maxQty'])
            # break


def get_maxQty(data):
    for filter in data['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            # step_size = float(filter['stepSize'])
            # min_qty = float(filter['minQty'])
            # max_qty = float(filter['maxQty'])
            return float(filter['maxQty'])
            # break


def get_precision(data):
    step_size = get_stepSize(data)

    return int(round((-math.log(step_size, 10)), 0))
