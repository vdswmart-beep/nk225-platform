# ideas/idea_explainer.py — FIXED (BUG-14: colonnes réelles utilisées, plus de colonnes fantômes)

import numpy as np


class IdeaExplainer:

    def _safe(self, row, key, default=None):
        """Accès sécurisé à une colonne qui peut ne pas exister."""
        val = row.get(key, default)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return val

    def build_thesis(self, row, side: str) -> str:
        ticker  = row.get("ticker", "?")
        score   = self._safe(row, "research_score", 50)
        roe     = self._safe(row, "roe")
        pe      = self._safe(row, "pe")
        mom_12m = self._safe(row, "mom_12m")
        vol     = self._safe(row, "vol_252d")

        parts = []

        if side == "LONG":
            if roe is not None and roe > 0.10:
                parts.append(f"ROE élevé ({roe:.1%})")
            if pe is not None and pe < 15:
                parts.append(f"valorisation attractive (PE {pe:.1f}x)")
            if mom_12m is not None and mom_12m > 0.05:
                parts.append(f"momentum positif sur 12M (+{mom_12m:.1%})")
            qualifier = " et ".join(parts) if parts else "profil fondamental solide"
            return (
                f"{ticker} présente un {qualifier}. "
                f"Score quantitatif : {score:.0f}/100. "
                f"Le marché sous-évalue probablement la qualité de ses fondamentaux."
            )
        else:
            if roe is not None and roe < 0.05:
                parts.append(f"ROE faible ({roe:.1%})")
            if pe is not None and pe > 30:
                parts.append(f"valorisation tendue (PE {pe:.1f}x)")
            if mom_12m is not None and mom_12m < -0.05:
                parts.append(f"momentum négatif sur 12M ({mom_12m:.1%})")
            qualifier = " et ".join(parts) if parts else "détérioration des fondamentaux"
            return (
                f"{ticker} présente un {qualifier}. "
                f"Score quantitatif : {score:.0f}/100. "
                f"La valorisation semble excessive par rapport aux fondamentaux."
            )

    def build_catalysts(self, row, side: str) -> list:
        catalysts = []

        mom_12m = self._safe(row, "mom_12m")
        mom_3m  = self._safe(row, "mom_3m")
        roe     = self._safe(row, "roe")
        fcf     = self._safe(row, "fcf_yield")
        pb      = self._safe(row, "pb")

        if side == "LONG":
            if mom_12m is not None and mom_12m > 0.10:
                catalysts.append(f"Momentum 12M fort : +{mom_12m:.1%}")
            if mom_3m is not None and mom_3m > 0.05:
                catalysts.append(f"Accélération récente 3M : +{mom_3m:.1%}")
            if roe is not None and roe > 0.12:
                catalysts.append(f"ROE supérieur au secteur : {roe:.1%}")
            if fcf is not None and fcf > 0.04:
                catalysts.append(f"Rendement FCF attractif : {fcf:.1%}")
        else:
            if mom_12m is not None and mom_12m < -0.05:
                catalysts.append(f"Tendance baissière 12M : {mom_12m:.1%}")
            if pb is not None and pb > 3.0:
                catalysts.append(f"Price-to-Book élevé : {pb:.1f}x — risque de rerating")
            if roe is not None and roe < 0.04:
                catalysts.append(f"ROE structurellement faible : {roe:.1%}")

        if not catalysts:
            catalysts.append("Potentiel de mean-reversion identifié par le modèle")

        return catalysts[:3]

    def build_risks(self, row, side: str) -> list:
        risks = []

        vol    = self._safe(row, "vol_252d")
        pe     = self._safe(row, "pe")
        pb     = self._safe(row, "pb")
        mom_3m = self._safe(row, "mom_3m")

        if vol is not None and vol > 0.35:
            risks.append(f"Volatilité annualisée élevée : {vol:.1%}")
        if side == "LONG":
            if mom_3m is not None and mom_3m < -0.05:
                risks.append(f"Momentum court terme négatif : {mom_3m:.1%}")
            if pe is not None and pe > 25:
                risks.append(f"Valorisation PE élevée : {pe:.1f}x")
        else:
            if mom_3m is not None and mom_3m > 0.10:
                risks.append(f"Rebond court terme possible : +{mom_3m:.1%}")
            if pb is not None and pb < 1.0:
                risks.append(f"Valorisation PB faible — potentiel support : {pb:.1f}x")

        if not risks:
            risks.append("Risque de marché général (macro Japon / USD/JPY)")

        return risks[:2]

    def explain(self, df, side: str, ranker) -> list:
        ideas = []
        for _, row in df.iterrows():
            idea = {
                "ticker":     row.get("ticker"),
                "score":      round(float(row.get("research_score", 0)), 2),
                "conviction": ranker.compute_conviction(float(row.get("research_score", 50))),
                "side":       side,
                "thesis":     self.build_thesis(row, side),
                "catalysts":  self.build_catalysts(row, side),
                "risks":      self.build_risks(row, side),
            }
            ideas.append(idea)
        return ideas