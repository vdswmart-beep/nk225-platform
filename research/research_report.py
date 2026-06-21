class ResearchReport:

    def __init__(
        self,
        ic_stats,
        test_stats,
        quantile_stats,
        regime_stats=None,
        capacity_stats=None
    ):
        self.ic = ic_stats
        self.tests = test_stats
        self.quantiles = quantile_stats
        self.regime = regime_stats
        self.capacity = capacity_stats

        # computed
        self.valid_factor = self._compute_validity()
        self.confidence_score = self._compute_confidence()

    def _compute_validity(self):
        return (
            self.ic["ic_mean"] > 0 and
            self.tests["t_test"]["p_value"] < 0.05 and
            self.quantiles["spread"] > 0
        )

    def _compute_confidence(self):
        icir = self.ic["icir"]
        spread = self.quantiles["spread"]
        hit = self.ic["hit_ratio"]

        return 0.4 * icir + 0.3 * spread + 0.3 * hit

    def to_dict(self):
        return {
            "valid_factor": self.valid_factor,
            "confidence_score": self.confidence_score,
            "statistics": {
                "ic": self.ic,
                "tests": self.tests,
                "quantiles": self.quantiles,
                "regime": self.regime,
                "capacity": self.capacity
            }
        }