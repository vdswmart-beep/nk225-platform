import numpy as np
import scipy.stats as stats

class StatisticalTests:

    @staticmethod
    def t_test(series):
        t_stat, p_value = stats.ttest_1samp(series, 0)
        return {"t_stat": t_stat, "p_value": p_value}

    @staticmethod
    def mann_whitney(group1, group2):
        stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        return {"stat": stat, "p_value": p_value}

    @staticmethod
    def anova(*groups):
        stat, p_value = stats.f_oneway(*groups)
        return {"stat": stat, "p_value": p_value}

    @staticmethod
    def jarque_bera(series):
        stat, p_value = stats.jarque_bera(series)
        return {"stat": stat, "p_value": p_value}

    @staticmethod
    def bootstrap_mean(series, n_bootstrap=1000):
        means = []
        n = len(series)

        for _ in range(n_bootstrap):
            sample = np.random.choice(series, size=n, replace=True)
            means.append(np.mean(sample))

        return {
            "mean": np.mean(means),
            "std": np.std(means),
            "ci_95": np.percentile(means, [2.5, 97.5])
        }