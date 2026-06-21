# pipelines/idea_pipeline.py

import logging
from dataclasses import dataclass, field
from typing import List
from ideas.ideas_orchestration import InvestmentPipeline, PipelineInputs, PipelineOutputs

logger = logging.getLogger("IdeaPipeline")


@dataclass
class IdeaOutputs:
    longs:       list = field(default_factory=list)
    shorts:      list = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)


class IdeaPipeline:

    def __init__(self, config: dict = None):
        self.pipeline = InvestmentPipeline(config or {})

    def run(self, features_wide, market_regime="neutral") -> IdeaOutputs:
        logger.info(f"Generating ideas — regime: {market_regime}")
        inputs = PipelineInputs(
            feature_matrix=features_wide,
            research_results=None,
            fundamentals=None,
            market_regime=market_regime,
        )
        out = self.pipeline.run(inputs)
        logger.info(f"Longs: {len(out.longs)} | Shorts: {len(out.shorts)}")
        return IdeaOutputs(longs=out.longs, shorts=out.shorts, diagnostics=out.diagnostics)
