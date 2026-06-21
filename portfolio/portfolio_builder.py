# portfolio/portfolio_builder.py — FIXED: accepte long_tickers / short_tickers

import numpy as np
from portfolio.portfolio_object import Portfolio
from portfolio.optimizer       import mean_variance_weights
from portfolio.risk_parity     import risk_parity_weights
from portfolio.hrp             import hrp_allocation
from portfolio.position_sizing import apply_constraints


def compute_metrics(weights, mu, cov):
    exp_return = weights @ mu
    exp_vol    = np.sqrt(np.clip(weights.T @ cov @ weights, 0, None))
    return exp_return, exp_vol


def compute_turnover(new_w, old_w):
    if old_w is None:
        return float(np.sum(np.abs(new_w)))
    return float(np.sum(np.abs(new_w - old_w)))


def build_portfolio(
    mu,
    cov,
    method        = "risk_parity",
    betas         = None,
    sectors       = None,
    prev_weights  = None,
    # ── Nouveaux paramètres P1-B (ignorés par les méthodes qui n'en ont pas besoin)
    long_tickers  = None,
    short_tickers = None,
    all_tickers   = None,
):
    """
    Construit un portefeuille avec la méthode demandée.

    Args:
        mu            : vecteur de rendements attendus (signé : négatif pour shorts)
        cov           : matrice de covariance (n×n)
        method        : "risk_parity" | "hrp" | "mean_variance" | "equal_weight"
        long_tickers  : liste des tickers côté LONG  (optionnel — pour info)
        short_tickers : liste des tickers côté SHORT (optionnel — pour info)
        all_tickers   : liste complète dans l'ordre de mu/cov (optionnel)
    """
    n = len(mu)

    if method == "equal_weight":
        w = np.ones(n) / n

    elif method == "risk_parity":
        w = risk_parity_weights(cov)

    elif method == "hrp":
        w = hrp_allocation(cov)

    elif method == "mean_variance":
        w = mean_variance_weights(mu, cov)

    else:
        raise ValueError(f"Méthode inconnue : '{method}'")

    # ── Application du signe SHORT ────────────────────────────────
    # Si des tickers sont marqués SHORT, on retourne leur poids
    if short_tickers and all_tickers:
        short_set = set(short_tickers)
        for i, ticker in enumerate(all_tickers):
            if ticker in short_set:
                w[i] = -abs(w[i])

    # ── Contraintes de poids ──────────────────────────────────────
    w = apply_constraints(w, betas, sectors)

    # ── Métriques ─────────────────────────────────────────────────
    exp_return, exp_vol = compute_metrics(w, mu, cov)
    turnover = compute_turnover(w, prev_weights)

    exposures = {
        "net":   float(np.sum(w)),
        "gross": float(np.sum(np.abs(w))),
        "beta":  float(np.dot(w, betas)) if betas is not None else None,
    }

    return Portfolio(
        weights            = w,
        exposures          = exposures,
        turnover           = turnover,
        expected_return    = float(exp_return),
        expected_volatility= float(exp_vol),
    )