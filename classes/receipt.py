class Receipt:
    def __init__(self) -> None:
        self.buy_receipt = None
        self.sell_receipt = None

    def getBuyReceipt(self, receipt) -> None:
        self.buy_receipt = receipt

    def getSellReceipt(self, receipt) -> None:
        self.sell_receipt = receipt

    def buyReceiptPrice(self) -> str:
        return float(self.buy_receipt['fills'][0]['price'])

    def buyReceiptQuantity(self) -> str:
        return float(self.buy_receipt['fills'][0]['qty'])
