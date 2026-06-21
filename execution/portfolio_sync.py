class PortfolioSync:

    def __init__(self, ib):
        self.ib = ib

    def get_positions(self):
        positions = self.ib.positions()
        result = {}

        for p in positions:
            symbol = p.contract.symbol
            result[symbol] = {
                "position": p.position,
                "avgCost": p.avgCost
            }

        return result

    def get_cash(self):
        summary = self.ib.accountSummary()
        for item in summary:
            if item.tag == "TotalCashValue":
                return float(item.value)
        return 0.0