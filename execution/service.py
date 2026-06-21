from execution.connection import IBConnection
from execution.market_data import MarketData
from execution.order_manager import OrderManager
from execution.portfolio_sync import PortfolioSync
from execution.execution_engine import ExecutionEngine


class ExecutionService:

    def __init__(self):
        self.ib = IBConnection.get_instance()

        self.market_data = MarketData(self.ib)
        self.portfolio_sync = PortfolioSync(self.ib)
        self.order_manager = OrderManager(self.ib)

        self.engine = ExecutionEngine(
            self.ib,
            self.portfolio_sync,
            self.order_manager,
            self.market_data
        )

    def execute_target_portfolio_market(self, target_portfolio):
        trades = self.engine.execute_market(target_portfolio)
        self.engine.wait_for_fills(trades)
        return trades

    def execute_target_portfolio_limit(self, target_portfolio):
        trades = self.engine.execute_limit(target_portfolio)
        self.engine.wait_for_fills(trades)
        return trades

    def get_current_portfolio(self):
        return self.portfolio_sync.get_positions()

    def get_cash(self):
        return self.portfolio_sync.get_cash()