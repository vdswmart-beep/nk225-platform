# pipelines/portfolio_pipeline.py — FIXED (BUG-09: poids SHORT négatifs réels)

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from portfolio.portfolio_builder import build_portfolio
from portfolio.portfolio_object import Portfolio
from config.settings import DEFAULT_METHOD, MAX_POSITION_WEIGHT, MIN_POSITION_WEIGHT

logger = logging.getLogger("PortfolioPipeline")


@dataclass
class PortfolioOutputs:
    portfolio: Portfolio = None
    weights:   dict      = None     # ticker → poids (négatif pour les shorts)
    longs:     list      = None     # liste des tickers long
    shorts:    list      = None     # liste des tickers short


class PortfolioPipeline:

    def run(
        self,
        returns:  pd.DataFrame,
        ideas:    list,
        method:   str = None,
    ) -> PortfolioOutputs:
        method = method or DEFAULT_METHOD
        logger.info(f"Construction du portefeuille — méthode: {method}")

        tickers = returns.columns.tolist()
        n       = len(tickers)

        # ── Identifier les côtés LONG / SHORT ────────────────────────────
        long_set  = {i["ticker"] for i in ideas if i.get("side") == "LONG"}
        short_set = {i["ticker"] for i in ideas if i.get("side") == "SHORT"}

        # Score par ticker (0-100 → z-scoré)
        score_map = {i["ticker"]: i.get("score", 50.0) for i in ideas}
        mu_raw    = np.array([float(score_map.get(t, 50.0)) for t in tickers])
        mu_z      = (mu_raw - mu_raw.mean()) / (mu_raw.std() + 1e-8)

        # FIX BUG-09: inverser le signe du mu pour les shorts
        # → le portefeuille optimisé leur attribuera des poids négatifs
        mu_signed = np.array([
            -abs(mu_z[i]) if tickers[i] in short_set
            else abs(mu_z[i]) if tickers[i] in long_set
            else 0.0
            for i in range(n)
        ])
        mu = 0.08 + 0.05 * mu_signed

        # ── Matrice de covariance ─────────────────────────────────────────
        cov = returns.cov().fillna(0).values
        if cov.shape[0] != n:
            cov = np.eye(n) * 0.04

        # ── Construction ─────────────────────────────────────────────────
        port = build_portfolio(
            mu=mu, cov=cov, method=method,
            long_tickers=list(long_set),
            short_tickers=list(short_set),
            all_tickers=tickers,
        )

        weights = {t: float(port.weights[i]) for i, t in enumerate(tickers)}

        longs_out  = [t for t, w in weights.items() if w > 1e-4]
        shorts_out = [t for t, w in weights.items() if w < -1e-4]

        logger.info(
            f"Portefeuille: {len(longs_out)} longs / {len(shorts_out)} shorts "
            f"| Gross: {port.gross_exposure():.2f} | Net: {port.net_exposure():.2f}"
        )

        return PortfolioOutputs(
            portfolio=port,
            weights=weights,
            longs=longs_out,
            shorts=shorts_out,
        )