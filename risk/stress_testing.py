import numpy as np


def apply_scenario(returns_df, shock_vector):
    return returns_df + shock_vector


def stress_2008(returns_df):
    shock = -0.05  # -5% daily proxy
    return apply_scenario(returns_df, shock)


def stress_covid(returns_df):
    shock = -0.07
    return apply_scenario(returns_df, shock)


def inflation_shock(returns_df):
    shock = -0.03
    return apply_scenario(returns_df, shock)


def rate_shock(returns_df):
    shock = -0.02
    return apply_scenario(returns_df, shock)


def evaluate_stress(returns_df, weights, scenario_func):
    stressed_returns = scenario_func(returns_df)
    portfolio_returns = stressed_returns @ weights
    return portfolio_returns.mean(), portfolio_returns.min()