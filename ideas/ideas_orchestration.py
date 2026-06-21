# ideas/orchestration.py

from dataclasses import dataclass
from typing import Dict, Any
import logging
import time

from ideas.idea_engine import IdeaEngine
from ideas.idea_scoring import IdeaScorer
from ideas.idea_ranking import IdeaRanker
from ideas.idea_explainer import IdeaExplainer


# =========================
# CONFIG & INPUT STRUCTURE
# =========================

@dataclass
class PipelineInputs:
    feature_matrix: Any
    research_results: Any
    fundamentals: Any
    market_regime: str


@dataclass
class PipelineOutputs:
    longs: list
    shorts: list
    diagnostics: Dict


# =========================
# ORCHESTRATOR
# =========================

class InvestmentPipeline:

    def __init__(self, config: Dict = None):
        self.config = config or {}

        # Modules
        self.engine = IdeaEngine(self.config.get("engine"))
        self.scorer = IdeaScorer(self.config.get("scorer"))
        self.ranker = IdeaRanker(**self.config.get("ranker", {}))
        self.explainer = IdeaExplainer()

        # Logger
        self.logger = logging.getLogger("InvestmentPipeline")
        self.logger.setLevel(logging.INFO)

    # =========================
    # PIPELINE STEPS
    # =========================

    def _generate_universe(self, inputs: PipelineInputs):
        return self.engine.generate(
            inputs.feature_matrix,
            inputs.research_results,
            inputs.fundamentals
        )

    def _score(self, df, market_regime):
        return self.scorer.compute_score(df, market_regime)

    def _rank(self, df):
        return self.ranker.rank(df)

    def _explain(self, longs_df, shorts_df):
        longs = self.explainer.explain(longs_df, "LONG", self.ranker)
        shorts = self.explainer.explain(shorts_df, "SHORT", self.ranker)
        return longs, shorts

    # =========================
    # HOOKS (EXTENSIBLE)
    # =========================

    def pre_process(self, inputs: PipelineInputs):
        return inputs

    def post_process(self, outputs: PipelineOutputs):
        return outputs

    # =========================
    # MAIN ENTRYPOINT
    # =========================

    def run(self, inputs: PipelineInputs) -> PipelineOutputs:

        start_time = time.time()
        diagnostics = {}

        try:
            self.logger.info("Pipeline started")

            # ---- PRE PROCESS ----
            inputs = self.pre_process(inputs)

            # ---- STEP 1: UNIVERSE ----
            t0 = time.time()
            df = self._generate_universe(inputs)
            diagnostics["universe_size"] = len(df)
            diagnostics["engine_time"] = time.time() - t0

            # ---- STEP 2: SCORING ----
            t0 = time.time()
            df = self._score(df, inputs.market_regime)
            diagnostics["scoring_time"] = time.time() - t0

            # ---- STEP 3: RANKING ----
            t0 = time.time()
            longs_df, shorts_df = self._rank(df)

            top_n = self.config.get("top_n", 10)
            longs_df = longs_df.head(top_n)
            shorts_df = shorts_df.head(top_n)

            diagnostics["ranking_time"] = time.time() - t0

            # ---- STEP 4: EXPLAIN ----
            t0 = time.time()
            longs, shorts = self._explain(longs_df, shorts_df)
            diagnostics["explain_time"] = time.time() - t0

            # ---- METRICS ----
            diagnostics["total_time"] = time.time() - start_time
            diagnostics["market_regime"] = inputs.market_regime

            outputs = PipelineOutputs(
                longs=longs,
                shorts=shorts,
                diagnostics=diagnostics
            )

            # ---- POST PROCESS ----
            outputs = self.post_process(outputs)

            self.logger.info("Pipeline completed successfully")

            return outputs

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise