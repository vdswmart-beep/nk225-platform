# pipelines/master_pipeline.py
#
# Orchestrates the full end-to-end pipeline:
#   Data → Features → Research → Ideas → Portfolio → Risk → (Execution)

import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional

from config.settings import BACKTEST_START, BACKTEST_END, DEFAULT_METHOD
from pipelines.data_pipeline      import DataPipeline,      DataOutputs
from pipelines.feature_pipeline   import FeaturePipeline,   FeatureOutputs
from pipelines.research_pipeline  import ResearchPipeline,  ResearchOutputs
from pipelines.idea_pipeline      import IdeaPipeline,      IdeaOutputs
from pipelines.portfolio_pipeline import PortfolioPipeline, PortfolioOutputs
from pipelines.risk_pipeline      import RiskPipeline,      RiskOutputs
from pipelines.execution_pipeline import ExecutionPipeline, ExecutionOutputs

logger = logging.getLogger("MasterPipeline")


@dataclass
class MasterOutputs:
    data:       DataOutputs      = None
    features:   FeatureOutputs   = None
    research:   ResearchOutputs  = None
    ideas:      IdeaOutputs      = None
    portfolio:  PortfolioOutputs = None
    risk:       RiskOutputs      = None
    execution:  ExecutionOutputs = None
    timings:    dict             = field(default_factory=dict)
    success:    bool             = False


class MasterPipeline:

    def __init__(
        self,
        data_service,
        tickers:        List[str],
        start:          str = BACKTEST_START,
        end:            str = BACKTEST_END,
        market_regime:  str = "neutral",
        portfolio_method: str = DEFAULT_METHOD,
        execution_service=None,
        mode:           str = "backtest",
    ):
        self.tickers          = tickers
        self.start            = start
        self.end              = end
        self.market_regime    = market_regime
        self.portfolio_method = portfolio_method
        self.mode             = mode

        self.data_pipe      = DataPipeline(data_service)
        self.feature_pipe   = FeaturePipeline()
        self.research_pipe  = ResearchPipeline()
        self.idea_pipe      = IdeaPipeline()
        self.portfolio_pipe = PortfolioPipeline()
        self.risk_pipe      = RiskPipeline()
        self.exec_pipe      = ExecutionPipeline(mode, execution_service)

    def _step(self, name: str, fn, timings: dict):
        t0 = time.time()
        logger.info(f"▶ {name}")
        result = fn()
        timings[name] = round(time.time() - t0, 2)
        logger.info(f"✓ {name} ({timings[name]}s)")
        return result

    def run(self) -> MasterOutputs:
        logger.info("=" * 60)
        logger.info("MASTER PIPELINE STARTED")
        logger.info(f"Universe: {len(self.tickers)} tickers | {self.start} → {self.end}")
        logger.info("=" * 60)

        out      = MasterOutputs()
        timings  = {}
        t_total  = time.time()

        try:
            out.data = self._step(
                "Data", lambda: self.data_pipe.run(self.tickers, self.start, self.end), timings
            )
            out.features = self._step(
                "Features", lambda: self.feature_pipe.run(out.data.prices, out.data.fundamentals), timings
            )
            out.research = self._step(
                "Research", lambda: self.research_pipe.run(out.features.features_long, out.data.returns), timings
            )
            out.ideas = self._step(
                "Ideas", lambda: self.idea_pipe.run(out.features.features_wide, self.market_regime), timings
            )
            all_ideas = out.ideas.longs + out.ideas.shorts
            out.portfolio = self._step(
                "Portfolio", lambda: self.portfolio_pipe.run(out.data.returns, all_ideas, self.portfolio_method), timings
            )
            out.risk = self._step(
                "Risk", lambda: self.risk_pipe.run(out.data.returns, out.portfolio.weights), timings
            )
            out.execution = self._step(
                "Execution", lambda: self.exec_pipe.run(out.portfolio.weights, nav=100_000_000), timings
            )

            out.timings = timings
            out.success = True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            out.timings = timings

        total = round(time.time() - t_total, 2)
        logger.info(f"MASTER PIPELINE COMPLETED in {total}s | success={out.success}")
        return out
