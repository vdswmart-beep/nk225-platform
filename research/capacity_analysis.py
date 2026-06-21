import numpy as np

class CapacityAnalysis:

    @staticmethod
    def turnover(weights):
        return np.abs(weights.diff()).sum().mean()

    @staticmethod
    def capacity_proxy(volume, weights):
        return (weights.abs() / volume).mean()

    @staticmethod
    def estimate_capacity(volume, signal_strength):
        return volume.mean() * signal_strength