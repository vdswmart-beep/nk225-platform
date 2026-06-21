# dashboard/callbacks/backtest_callbacks.py — P3: Callbacks Backtest Lab

import io
import logging
import pandas as pd
import numpy as np
from datetime import datetime

from dash import Input, Output, State, callback, no_update, dcc
from dash.exceptions import PreventUpdate

from dashboard.components.charts import (
    line_chart, area_fill_chart, bar_chart, empty_fig,
)

logger = logging.getLogger("BacktestCallbacks")


def _make_monthly_heatmap(daily_returns: pd.Series):
    """Heatmap PnL mensuel sous forme de bar chart groupé."""
    import plotly.graph_objects as go

    monthly = daily_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    monthly.index = pd.to_datetime(monthly.index)

    colors = ["#3fb950" if v >= 0 else "#f85149" for v in monthly.values]
    fig = go.Figure(go.Bar(
        x=[d.strftime("%Y-%m") for d in monthly.index],
        y=monthly.values * 100,
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:.2f}%</b><extra></extra>",
    ))
    _BG   = "#0f141b"
    _GRID = "rgba(255,255,255,0.04)"
    _TEXT = "#8899aa"
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_BG,
        font=dict(family="Inter, system-ui", color=_TEXT, size=11),
        margin=dict(l=40, r=16, t=28, b=40),
        height=200,
        xaxis=dict(gridcolor=_GRID, tickfont=dict(size=9)),
        yaxis=dict(gridcolor=_GRID, ticksuffix="%",
                   tickfont=dict(size=10), zeroline=True,
                   zerolinecolor="#334455"),
        bargap=0.2,
    )
    return fig


def register_backtest_callbacks(app, dp):
    """Enregistre les callbacks du Backtest Lab."""

    @app.callback(
        Output("bt-status",      "children"),
        Output("bt-kpi-sharpe",  "children"),
        Output("bt-kpi-sortino", "children"),
        Output("bt-kpi-return",  "children"),
        Output("bt-kpi-maxdd",   "children"),
        Output("bt-kpi-winrate", "children"),
        Output("bt-kpi-calmar",  "children"),
        Output("bt-equity-fig",  "figure"),
        Output("bt-dd-fig",      "figure"),
        Output("bt-sharpe-fig",  "figure"),
        Output("bt-monthly-fig", "figure"),
        Input("bt-run-btn",      "n_clicks"),
        State("bt-train-months", "value"),
        State("bt-test-months",  "value"),
        State("bt-strategy",     "value"),
        prevent_initial_call=True,
    )
    def run_backtest(n_clicks, train_months, test_months, strategy):
        if not n_clicks:
            raise PreventUpdate

        empty = [empty_fig()] * 4
        defaults = ["—"] * 6

        try:
            # Chargement rendements
            returns = dp.get_returns()
            if returns is None or returns.empty:
                return ("Données non disponibles",) + tuple(defaults) + tuple(empty)

            # Choix pipeline
            from backtesting.backtest_engine import (
                BacktestEngine, equal_weight_pipeline, momentum_pipeline,
            )
            if strategy == "momentum":
                top_n = max(3, len(returns.columns) // 5)
                fn    = lambda r: momentum_pipeline(r, top_n=top_n)
            else:
                fn = equal_weight_pipeline

            engine = BacktestEngine(
                train_months=train_months or 12,
                test_months=test_months  or 3,
                slippage_bps=5.0,
                cost_bps=3.0,
            )
            result = engine.run(returns, fn)

            # Stocker sur dp pour export
            dp._last_backtest = result

            m = result.metrics

            def fmt_pct(v): return f"{v:.2%}" if v is not None else "—"
            def fmt_f(v):   return f"{v:.3f}"  if v is not None else "—"

            status = (
                f"✓ Walk-forward terminé — {len(result.windows)} fenêtres | "
                f"{len(result.daily_returns)} jours out-of-sample"
            )

            # ── Equity curve ──────────────────────────────────────
            eq_df = result.equity_curve.reset_index()
            eq_df.columns = ["date", "nav"]
            eq_df["index_100"] = eq_df["nav"] / eq_df["nav"].iloc[0] * 100
            equity_fig = line_chart(eq_df, "date", "index_100",
                                    title="Equity Curve (Base 100)",
                                    color="#4a9eff", height=280)

            # ── Drawdown ──────────────────────────────────────────
            dd_df = result.drawdown_series.reset_index()
            dd_df.columns = ["date", "dd"]
            dd_fig = area_fill_chart(dd_df, "date", "dd",
                                     title="Drawdown", height=200)

            # ── Rolling Sharpe ────────────────────────────────────
            rs_df = result.rolling_sharpe.dropna().reset_index()
            rs_df.columns = ["date", "sharpe"]
            sharpe_fig = line_chart(rs_df, "date", "sharpe",
                                    title="Rolling Sharpe (63j)",
                                    color="#60c4cc", height=200)

            # ── Monthly PnL ───────────────────────────────────────
            monthly_fig = _make_monthly_heatmap(result.daily_returns)

            return (
                status,
                fmt_f(m.get("sharpe")),
                fmt_f(m.get("sortino")),
                fmt_pct(m.get("ann_return")),
                fmt_pct(m.get("max_drawdown")),
                fmt_pct(m.get("win_rate")),
                fmt_f(m.get("calmar")),
                equity_fig, dd_fig, sharpe_fig, monthly_fig,
            )

        except Exception as e:
            logger.error(f"Backtest callback error: {e}", exc_info=True)
            msg = f"Erreur : {e}"
            return (msg,) + tuple(defaults) + tuple(empty)

    # ── Export Excel ──────────────────────────────────────────────
    @app.callback(
        Output("bt-download",       "data"),
        Output("bt-export-status",  "children"),
        Input("bt-export-btn",      "n_clicks"),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        result = getattr(dp, "_last_backtest", None)
        if result is None:
            return no_update, "⚠ Lancez d'abord un backtest"

        try:
            from reporting.excel_exporter import export_track_record
            import tempfile, os

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                tmp_path = tmp.name

            export_track_record(result, output_path=tmp_path)

            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)

            date_str  = datetime.now().strftime("%Y%m%d")
            filename  = f"NK225_track_record_{date_str}.xlsx"

            return (
                dcc.send_bytes(data, filename),
                f"✓ {filename} prêt au téléchargement",
            )
        except Exception as e:
            logger.error(f"Export Excel failed: {e}")
            return no_update, f"⚠ Erreur export : {e}"