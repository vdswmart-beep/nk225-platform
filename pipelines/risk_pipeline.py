# pipelines/risk_pipeline.py

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from risk.var import portfolio_var, portfolio_cvar
from risk.drawdown import max_drawdown, compute_drawdown
from risk.stress_testing import evaluate_stress, stress_2008, stress_covid, inflation_shock, rate_shock

logger = logging.getLogger("RiskPipeline")


@dataclass
class RiskOutputs:
    var:          float = 0.0
    cvar:         float = 0.0
    max_drawdown: float = 0.0
    ann_vol:      float = 0.0
    sharpe:       float = 0.0
    stress_tests: dict  = field(default_factory=dict)
    drawdown_series: pd.Series = field(default_factory=pd.Series)


class RiskPipeline:

    def run(self, returns: pd.DataFrame, weights: dict) -> RiskOutputs:
        logger.info("Computing risk metrics...")
        out = RiskOutputs()

        tickers = [t for t in weights if t in returns.columns]
        w = np.array([weights[t] for t in tickers])
        if w.sum() > 0:
            w /= w.sum()
        sub = returns[tickers].dropna()

        try:
            out.var  = portfolio_var(sub, w)
            out.cvar = portfolio_cvar(sub, w)
            port_ret = sub @ w
            nav = (1 + port_ret).cumprod()
            out.drawdown_series = compute_drawdown(nav)
            out.max_drawdown    = float(out.drawdown_series.min())
            out.ann_vol         = float(port_ret.std() * np.sqrt(252))
            out.sharpe = float(port_ret.mean() / port_ret.std() * np.sqrt(252)) if port_ret.std() > 0 else 0

            out.stress_tests = {
                "2008":      evaluate_stress(sub, w, stress_2008),
                "COVID":     evaluate_stress(sub, w, stress_covid),
                "Inflation": evaluate_stress(sub, w, inflation_shock),
                "Rates":     evaluate_stress(sub, w, rate_shock),
            }
        except Exception as e:
            logger.error(f"Risk computation failed: {e}")

        return out
