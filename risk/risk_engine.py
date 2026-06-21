# risk/risk_engine.py — FIXED (BUG-01: corrected absolute imports)

from risk.var import portfolio_var, portfolio_cvar
from risk.drawdown import max_drawdown
from risk.factor_exposure import portfolio_beta, factor_exposure, sector_exposure
from risk.stress_testing import (
    evaluate_stress, stress_2008, stress_covid, inflation_shock, rate_shock
)
import logging

logger = logging.getLogger("RiskEngine")


class RiskEngine:

    def __init__(self, returns, prices, weights,
                 market_returns, factor_data, sector_map):
        self.returns = returns
        self.prices = prices
        self.weights = weights
        self.market_returns = market_returns
        self.factor_data = factor_data
        self.sector_map = sector_map

    def compute_risk(self):
        report = {}

        try:
            report["VaR"] = portfolio_var(self.returns, self.weights)
            report["CVaR"] = portfolio_cvar(self.returns, self.weights)
        except Exception as e:
            logger.warning(f"VaR/CVaR failed: {e}")
            report["VaR"] = report["CVaR"] = None

        try:
            portfolio_prices = (self.returns @ self.weights).cumsum()
            report["Max Drawdown"] = max_drawdown(portfolio_prices)
        except Exception as e:
            logger.warning(f"Drawdown failed: {e}")
            report["Max Drawdown"] = None

        try:
            report["Beta"] = portfolio_beta(
                self.returns, self.weights, self.market_returns
            )
        except Exception as e:
            logger.warning(f"Beta failed: {e}")
            report["Beta"] = None

        try:
            report["Factor Exposure"] = factor_exposure(
                self.returns, self.factor_data
            ).to_dict()
        except Exception as e:
            logger.warning(f"Factor exposure failed: {e}")
            report["Factor Exposure"] = {}

        try:
            report["Sector Exposure"] = sector_exposure(
                dict(zip(self.returns.columns, self.weights)),
                self.sector_map
            )
        except Exception as e:
            logger.warning(f"Sector exposure failed: {e}")
            report["Sector Exposure"] = {}

        try:
            report["Stress Tests"] = {
                "2008":      evaluate_stress(self.returns, self.weights, stress_2008),
                "COVID":     evaluate_stress(self.returns, self.weights, stress_covid),
                "Inflation": evaluate_stress(self.returns, self.weights, inflation_shock),
                "Rate Shock":evaluate_stress(self.returns, self.weights, rate_shock),
            }
        except Exception as e:
            logger.warning(f"Stress tests failed: {e}")
            report["Stress Tests"] = {}

        return report
