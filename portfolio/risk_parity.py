# risk_parity.py

import numpy as np

def risk_contribution(weights, cov):
    portfolio_var = weights.T @ cov @ weights
    marginal_contrib = cov @ weights
    return weights * marginal_contrib / portfolio_var


def risk_parity_weights(cov, max_iter=1000, tol=1e-6):
    n = cov.shape[0]
    w = np.ones(n) / n

    for _ in range(max_iter):
        rc = risk_contribution(w, cov)
        target = np.mean(rc)
        diff = rc - target

        if np.linalg.norm(diff) < tol:
            break

        w -= 0.01 * diff
        w = np.maximum(w, 1e-6)
        w /= np.sum(w)

    return w