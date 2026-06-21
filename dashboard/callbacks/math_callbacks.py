# dashboard/callbacks/math_callbacks.py — IDs corrigés pour correspondre à math_lab.py

import logging
import numpy as np
import pandas as pd
from dash import Input, Output, State, no_update
import plotly.graph_objects as go

from dashboard.components.charts import line_chart, bar_chart, correlation_heatmap, empty_fig
from math_engine.statistical_models import (
    ols_factor_regression, pca_analysis, rolling_factor_exposure,
)
from math_engine.hypothesis_testing import adf_test, jarque_bera_test, t_test_mean, cointegration_test

logger = logging.getLogger("MathCallbacks")
_BG = "#0f141b"; _GRID = "rgba(255,255,255,0.04)"; _TEXT = "#8899aa"


def register_math_callbacks(app, dp):

    @app.callback(
        Output("math-chart-output", "children"),   # ID page : math-chart-output
        Output("math-stats-output", "children"),   # ID page : math-stats-output
        Output("math-corr-output",  "children"),   # ID page : math-corr-output
        Output("math-pca-output",   "children"),   # ID page : math-pca-output
        Output("math-beta-output",  "children"),   # ID page : math-beta-output
        Input("math-run-btn",       "n_clicks"),
        State("math-ticker-a",      "value"),
        State("math-ticker-b",      "value"),
        State("math-factor",        "value"),
        State("math-method",        "value"),
        State("math-test",          "value"),      # ID page : math-test
        prevent_initial_call=True,
    )
    def run_math(n_clicks, ticker_a, ticker_b, factor, method, stat_test):
        from dash import html, dcc

        def _graph(fig):
            return dcc.Graph(figure=fig, config={"displayModeBar": False})

        def _txt(msg, color="#c0ccd8"):
            return html.Div(msg, style={"fontSize":"11px","color":color,
                                        "fontFamily":"JetBrains Mono, monospace",
                                        "whiteSpace":"pre-wrap","lineHeight":"1.7"})

        if not ticker_a:
            empty = _graph(empty_fig())
            return _txt("Sélectionner Ticker A"), _txt(""), empty, empty, empty

        try:
            returns = dp.get_returns()
            if returns is None or returns.empty:
                empty = _graph(empty_fig(message="Données non disponibles"))
                return _txt("Données vides"), _txt(""), empty, empty, empty

            # ── OLS / Chart principal ─────────────────────────────────
            chart_text = ""
            if (ticker_a in returns.columns and ticker_b
                    and ticker_b in returns.columns and method == "OLS Regression"):
                try:
                    res = ols_factor_regression(returns[ticker_a], returns[[ticker_b]])
                    beta  = res["betas"].get(ticker_b, 0)
                    alpha = res["alpha"]
                    r2    = res["r_squared"]
                    chart_text = (
                        f"OLS — {ticker_a} ~ {ticker_b}\n\n"
                        f"β  (beta)  = {beta:.4f}\n"
                        f"α  (alpha) = {alpha:.6f}\n"
                        f"R²         = {r2:.4f}\n"
                        f"N obs      = {res['n_obs']}\n\n"
                        f"t-stat β   = {list(res['t_stats'].values())[0]:.3f}\n"
                        f"p-value β  = {list(res['p_values'].values())[0]:.4f}"
                    )
                except Exception as e:
                    chart_text = f"Erreur OLS : {e}"
            elif method == "Rolling Beta" and ticker_b and ticker_b in returns.columns:
                try:
                    rb  = rolling_factor_exposure(returns[ticker_a], returns[ticker_b], window=63)
                    rb  = rb.reset_index(); rb.columns = ["date","beta","alpha"]
                    fig = line_chart(rb, "date", "beta",
                                     title=f"Rolling Beta 63j — {ticker_a} vs {ticker_b}",
                                     height=260, color="#4a9eff")
                    return _graph(fig), _txt(""), _graph(empty_fig()), _graph(empty_fig()), _graph(empty_fig())
                except Exception as e:
                    chart_text = f"Erreur Rolling Beta : {e}"
            else:
                chart_text = f"Méthode sélectionnée : {method}\nTicker A : {ticker_a}"

            chart_out = _txt(chart_text)

            # ── Test statistique ──────────────────────────────────────
            stat_out = _txt("Sélectionner un ticker et un test")
            if ticker_a in returns.columns:
                series = returns[ticker_a].dropna()
                try:
                    if stat_test == "ADF (Stationarity)":
                        r = adf_test(series)
                        stat_out = _txt(
                            f"ADF Test — {ticker_a}\n\n"
                            f"ADF stat    = {r['adf_stat']:.4f}\n"
                            f"p-value     = {r['p_value']:.4f}\n"
                            f"Lags        = {r['n_lags']}\n"
                            f"Critique 1% = {r['critical_1%']:.4f}\n"
                            f"Critique 5% = {r['critical_5%']:.4f}\n\n"
                            f"→ {'STATIONNAIRE ✓' if r['is_stationary'] else 'NON STATIONNAIRE ✗'}"
                        )
                    elif stat_test == "Jarque-Bera (Normality)":
                        r = jarque_bera_test(series)
                        stat_out = _txt(
                            f"Jarque-Bera — {ticker_a}\n\n"
                            f"JB stat  = {r['jb_stat']:.4f}\n"
                            f"p-value  = {r['p_value']:.4f}\n"
                            f"Skewness = {r['skewness']:.4f}\n"
                            f"Kurtosis = {r['kurtosis']:.4f}\n\n"
                            f"→ {'NORMALE ✓' if r['is_normal'] else 'NON NORMALE ✗'}"
                        )
                    elif stat_test == "T-Test (Mean=0)":
                        r = t_test_mean(series)
                        stat_out = _txt(
                            f"T-Test (μ=0) — {ticker_a}\n\n"
                            f"t stat  = {r['t_stat']:.4f}\n"
                            f"p-value = {r['p_value']:.4f}\n"
                            f"μ       = {r['mean']:.6f}\n"
                            f"σ       = {r['std']:.6f}\n"
                            f"N obs   = {r['n_obs']}\n\n"
                            f"→ {'SIGNIFICATIF ✓' if r['significant'] else 'NON SIGNIFICATIF ✗'}"
                        )
                    elif stat_test == "Bootstrap CI":
                        from math_engine.hypothesis_testing import bootstrap_ci
                        r = bootstrap_ci(series)
                        stat_out = _txt(
                            f"Bootstrap CI 95% — {ticker_a}\n\n"
                            f"Point estimate = {r['point_estimate']:.6f}\n"
                            f"CI lower       = {r['ci_lower']:.6f}\n"
                            f"CI upper       = {r['ci_upper']:.6f}\n"
                            f"Std error      = {r['std_error']:.6f}\n"
                            f"N bootstrap    = {r['n_bootstrap']}"
                        )
                except Exception as e:
                    stat_out = _txt(f"Erreur {stat_test} : {e}", color="#f85149")

            # ── Corrélation ───────────────────────────────────────────
            try:
                corr_fig = correlation_heatmap(returns.corr(), title="Return Correlation Matrix", height=300)
                corr_out = _graph(corr_fig)
            except Exception as e:
                corr_out = _graph(empty_fig(message=f"Erreur corrélation : {e}"))

            # ── PCA ───────────────────────────────────────────────────
            try:
                clean = returns.dropna(axis=0)
                if clean.shape[1] >= 2 and clean.shape[0] >= 5:
                    pca = pca_analysis(clean, n_components=min(5, clean.shape[1]))
                    ev  = pca["explained_variance"]
                    df_pca = pd.DataFrame({"PC":[f"PC{i+1}" for i in range(len(ev))],
                                           "var":[v*100 for v in ev]})
                    pca_fig = bar_chart(df_pca,"PC","var",title="PCA — Explained Variance (%)",
                                        color="#4a9eff",height=220)
                    pca_out = _graph(pca_fig)
                else:
                    pca_out = _graph(empty_fig(message="Pas assez de données"))
            except Exception as e:
                pca_out = _graph(empty_fig(message=f"Erreur PCA : {e}"))

            # ── Rolling Beta ──────────────────────────────────────────
            beta_out = _graph(empty_fig(message="Sélectionner Ticker A et Ticker B"))
            if ticker_b and ticker_a in returns.columns and ticker_b in returns.columns:
                try:
                    rb  = rolling_factor_exposure(returns[ticker_a], returns[ticker_b], window=63)
                    rb  = rb.reset_index(); rb.columns = ["date","beta","alpha"]
                    beta_out = _graph(line_chart(rb, "date", "beta",
                        title=f"Rolling Beta 63j — {ticker_a} vs {ticker_b}",
                        height=220, color="#60c4cc"))
                except Exception as e:
                    beta_out = _graph(empty_fig(message=f"Erreur : {e}"))

            return chart_out, stat_out, corr_out, pca_out, beta_out

        except Exception as e:
            logger.error(f"Math callback: {e}", exc_info=True)
            empty = lambda: __import__('dash', fromlist=['dcc']).dcc.Graph(figure=empty_fig())
            return f"Erreur : {e}", "", empty(), empty(), empty()