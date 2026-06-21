from ib_insync import Stock

class MarketData:

    def __init__(self, ib):
        self.ib = ib

    def get_last_price(self, symbol, exchange='SMART', currency='USD'):
        contract = Stock(symbol, exchange, currency)
        ticker = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(1)
        return ticker.last

    def get_bid_ask(self, symbol, exchange='SMART', currency='USD'):
        contract = Stock(symbol, exchange, currency)
        ticker = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(1)
        return ticker.bid, ticker.ask