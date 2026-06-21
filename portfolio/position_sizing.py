import numpy as np

def apply_constraints(
    weights,
    betas=None,
    sectors=None,
    max_weight=0.10,
    min_weight=-0.10
    ):
    """
    Simple portfolio constraints.
    
    ```
    Parameters
    ----------
    weights : np.ndarray
    betas : np.ndarray | None
    sectors : array-like | None
    max_weight : float
    min_weight : float
    
    Returns
    -------
    np.ndarray
    """
    
    weights = np.clip(
        weights,
        min_weight,
        max_weight
    )
    
    total = np.sum(np.abs(weights))
    
    if total > 0:
        weights = weights / total
    
    return weights
   