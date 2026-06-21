class Portfolio:
    def __init__(self,
                 weights,
                 exposures,
                 turnover,
                 expected_return,
                 expected_volatility,
                 metadata=None):

        self.weights = weights
        self.exposures = exposures
        self.turnover = turnover
        self.expected_return = expected_return
        self.expected_volatility = expected_volatility

        self.metadata = metadata or {}

    def gross_exposure(self):
        return abs(self.weights).sum()

    def net_exposure(self):
        return self.weights.sum()

    def summary(self):
        return {
            "gross": self.gross_exposure(),
            "net": self.net_exposure(),
            "turnover": self.turnover,
            "expected_return": self.expected_return,
            "expected_volatility": self.expected_volatility
        }