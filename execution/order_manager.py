from ib_insync import MarketOrder, LimitOrder, Stock

class OrderManager:

    def __init__(self, ib):
        self.ib = ib

    def _contract(self, symbol):
        return Stock(symbol, 'SMART', 'USD')

    def place_market_order(self, symbol, quantity):
        action = 'BUY' if quantity > 0 else 'SELL'
        order = MarketOrder(action, abs(quantity))
        contract = self._contract(symbol)

        trade = self.ib.placeOrder(contract, order)
        return trade

    def place_limit_order(self, symbol, quantity, limit_price):
        action = 'BUY' if quantity > 0 else 'SELL'
        order = LimitOrder(action, abs(quantity), limit_price)
        contract = self._contract(symbol)

        trade = self.ib.placeOrder(contract, order)
        return trade

    def get_open_orders(self):
        return self.ib.openTrades()

    def cancel_order(self, trade):
        self.ib.cancelOrder(trade.order)