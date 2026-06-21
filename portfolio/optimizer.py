# optimizer.py

import numpy as np


def mean_variance_weights(mu, cov, risk_aversion=1.0):
    inv_cov = np.linalg.pinv(cov)
    w = inv_cov @ mu
    w = w / np.sum(np.abs(w))
    return w