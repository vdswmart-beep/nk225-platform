# pipelines/execution_pipeline.py

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("ExecutionPipeline")


@dataclass
class ExecutionOutputs:
    trades:  list = field(default_factory=list)
    deltas:  dict = field(default_factory=dict)
    success: bool = False


class ExecutionPipeline:
    """Wraps ExecutionService for live trading. No-op in backtest mode."""

    def __init__(self, mode: str = "backtest", execution_service=None):
        self.mode = mode
        self.service = execution_service

    def run(self, target_weights: dict, nav: float, order_type: str = "limit") -> ExecutionOutputs:
        out = ExecutionOutputs()

        if self.mode == "backtest":
            logger.info("Backtest mode — execution skipped")
            out.deltas  = target_weights
            out.success = True
            return out

        if self.service is None:
            logger.error("ExecutionService not provided for live mode")
            return out

        target_portfolio = {t: int(w * nav) for t, w in target_weights.items()}
        try:
            if order_type == "limit":
                out.trades = self.service.execute_target_portfolio_limit(target_portfolio)
            else:
                out.trades = self.service.execute_target_portfolio_market(target_portfolio)
            out.success = True
            logger.info(f"Executed {len(out.trades)} trades")
        except Exception as e:
            logger.error(f"Execution failed: {e}")

        return out
