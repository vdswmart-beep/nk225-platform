# ideas/idea_scoring.py — FIXED (BUG-10: regime weights always renormalised to 1.0)

import numpy as np
import pandas as pd


class IdeaScorer:

    def __init__(self, weights=None):
        self.weights = weights or {
            "quality":   0.25,
            "growth":    0.20,
            "valuation": 0.20,
            "momentum":  0.20,
            "risk":      0.15,
        }

    def normalize(self, series):
        series = pd.to_numeric(series, errors="coerce")
        if series.isna().all():
            return np.zeros(len(series))
        std = series.std()
        if std == 0 or pd.isna(std):
            return np.zeros(len(series))
        return (series - series.mean()) / (std + 1e-8)

    def _regime_weights(self, base: dict, market_regime: str) -> dict:
        """Adjust weights for market regime, then renormalise so they sum to 1.0."""
        w = base.copy()
        if market_regime == "risk_on":
            w["momentum"]  += 0.10
            w["valuation"] -= 0.05
        elif market_regime == "risk_off":
            w["quality"] += 0.10
            w["risk"]    += 0.05
        # FIX: always renormalise
        total = sum(w.values())
        return {k: v / total for k, v in w.items()}

    def compute_score(self, df, market_regime="neutral"):
        df = df.copy()

        df["quality_z"]   = self.normalize(df.get("roe"))
        df["growth_z"]    = self.normalize(df.get("revenue_growth"))
        df["valuation_z"] = -self.normalize(df.get("pe"))

        momentum_col = "mom_12m" if "mom_12m" in df.columns else "mom_6m"
        df["momentum_z"] = self.normalize(df.get(momentum_col))

        risk_col = "vol_252d" if "vol_252d" in df.columns else "vol_63d"
        df["risk_z"] = -self.normalize(df.get(risk_col))

        score_cols = ["quality_z", "growth_z", "valuation_z", "momentum_z", "risk_z"]
        df[score_cols] = (
            df[score_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
        )

        w = self._regime_weights(self.weights, market_regime)

        df["raw_score"] = (
            w["quality"]   * df["quality_z"]
            + w["growth"]    * df["growth_z"]
            + w["valuation"] * df["valuation_z"]
            + w["momentum"]  * df["momentum_z"]
            + w["risk"]      * df["risk_z"]
        )

        mn, mx = df["raw_score"].min(), df["raw_score"].max()
        if pd.isna(mn) or pd.isna(mx) or (mx - mn) < 1e-8:
            df["research_score"] = 50.0
        else:
            df["research_score"] = 100.0 * (df["raw_score"] - mn) / (mx - mn)

        return df
