# portfolio/hrp.py — FIXED (BUG-06/07: condensed distance matrix + weight reordering)

import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform


def correl_dist(corr):
    dist = np.sqrt(np.clip(0.5 * (1 - corr), 0, 1))
    np.fill_diagonal(dist, 0)
    return dist


def hrp_allocation(cov):
    n = cov.shape[0]

    # Guard: if n==1 return trivially
    if n == 1:
        return np.array([1.0])

    corr = np.corrcoef(cov)
    dist_matrix = correl_dist(corr)

    # FIX BUG-06: scipy.linkage needs condensed 1-D array, not square matrix
    condensed = squareform(dist_matrix, checks=False)
    link = sch.linkage(condensed, method="single")

    sort_ix = sch.leaves_list(link)
    cov_sorted = cov[np.ix_(sort_ix, sort_ix)]

    w = np.ones(n)

    def _cluster_var(indices):
        sub = cov_sorted[np.ix_(indices, indices)]
        ivp = 1.0 / np.maximum(np.diag(sub), 1e-12)
        ivp /= ivp.sum()
        return float(ivp @ sub @ ivp)

    def _bisect(indices):
        if len(indices) <= 1:
            return
        mid = len(indices) // 2
        left, right = indices[:mid], indices[mid:]
        v1, v2 = _cluster_var(left), _cluster_var(right)
        alpha = 1.0 - v1 / (v1 + v2)
        w[left] *= alpha
        w[right] *= (1 - alpha)
        _bisect(left)
        _bisect(right)

    _bisect(list(range(n)))

    # FIX BUG-07: map weights from sorted space back to original ticker order
    w_original = np.empty(n)
    for sorted_pos, orig_pos in enumerate(sort_ix):
        w_original[orig_pos] = w[sorted_pos]

    w_original = np.maximum(w_original, 1e-8)
    w_original /= w_original.sum()
    return w_original
