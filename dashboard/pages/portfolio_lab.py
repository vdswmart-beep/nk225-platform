# dashboard/pages/portfolio_lab.py — FIXED: get_portfolio() retourne (nav_df, dict)

from dash import html, dcc, get_app
from dashboard.components.charts import line_chart, donut_chart
from dashboard.components.tables import base_table
import pandas as pd
import numpy as np

_CARD  = {"backgroundColor":"#0f141b","border":"1px solid #1e2a38","borderRadius":"8px","padding":"16px","marginBottom":"14px"}
_LABEL = {"fontSize":"10px","color":"#7eb8d8","textTransform":"uppercase","letterSpacing":".08em","marginBottom":"8px","fontWeight":"600"}


def layout():
    app = get_app()
    dp  = app.data_provider

    # get_portfolio() retourne (nav_df, weights_dict)
    try:
        nav_df, weights_dict = dp.get_portfolio()
        # weights_dict est un dict {ticker: float}
        if not isinstance(weights_dict, dict):
            weights_dict = {}
    except Exception as e:
        nav_df = pd.DataFrame(columns=["date","nav"])
        weights_dict = {}

    # Positions DataFrame depuis weights_dict
    try:
        df_positions = dp.get_positions_df()
    except Exception:
        if weights_dict:
            rows = [{"ticker":t,"weight":round(v,4),"side":"LONG" if v>0 else "SHORT",
                     "weight_pct":f"{v:.2%}"} for t,v in weights_dict.items() if abs(v)>1e-5]
            df_positions = pd.DataFrame(rows)
        else:
            df_positions = pd.DataFrame(columns=["ticker","weight","side","weight_pct"])

    try:
        kpis = dp.get_portfolio_kpis()
    except Exception:
        kpis = {}

    # Donut chart labels/values
    labels  = df_positions["ticker"].tolist() if not df_positions.empty else []
    weights_vals = (df_positions["weight"].abs() * 100).tolist() if not df_positions.empty else []

    def fmt(v, suffix="", decimals=2):
        if v is None: return "—"
        try:
            return f"{float(v):.{decimals}f}{suffix}"
        except Exception:
            return "—"

    nav_val   = kpis.get("nav", 0)
    nav_fmt   = f"¥{nav_val/1e6:.1f}M" if nav_val else "—"
    tr_val    = kpis.get("total_ret", 0)
    tr_fmt    = f"{tr_val:+.2f}%" if tr_val else "—"
    tr_class  = "kpi-positive" if (tr_val or 0) >= 0 else "kpi-negative"

    return html.Div([
        html.Div("Portfolio", style={**_LABEL,"fontSize":"11px","letterSpacing":".1em","marginBottom":"18px"}),

        # KPIs
        html.Div(className="grid", children=[
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("NAV", className="kpi-label"),
                    html.Div(nav_fmt, className="kpi-value"),
                    html.Div(f"{tr_fmt} total", className=f"kpi-sub {tr_class}"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("Sharpe Ratio", className="kpi-label"),
                    html.Div(fmt(kpis.get("sharpe")), className="kpi-value"),
                    html.Div("Annualisé", className="kpi-sub kpi-neutral"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("Volatilité Ann.", className="kpi-label"),
                    html.Div(fmt(kpis.get("vol"), "%"), className="kpi-value"),
                    html.Div("Réalisée", className="kpi-sub kpi-neutral"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("Max Drawdown", className="kpi-label"),
                    html.Div(fmt(kpis.get("max_dd"), "%"), className="kpi-value kpi-negative"),
                    html.Div(f"{kpis.get('n_longs',0)}L / {kpis.get('n_shorts',0)}S positions",
                             className="kpi-sub kpi-neutral"),
                ])
            ]),
        ]),

        html.Div(style={"height":"12px"}),

        # NAV + Donut
        html.Div(className="grid", children=[
            html.Div(className="panel col-8", children=[
                html.Div("NAV PERFORMANCE", style=_LABEL),
                dcc.Graph(
                    figure=line_chart(
                        nav_df if not nav_df.empty else pd.DataFrame(columns=["date","nav"]),
                        "date", "nav", title="NAV", height=240,
                    ),
                    config={"displayModeBar":False},
                ),
            ]),
            html.Div(className="panel col-4", children=[
                html.Div("ALLOCATION (GROSS)", style=_LABEL),
                dcc.Graph(
                    figure=donut_chart(labels, weights_vals, height=240) if labels else
                           donut_chart(["No data"],[1], height=240),
                    config={"displayModeBar":False},
                ),
            ]),
        ]),

        html.Div(style={"height":"12px"}),

        # Positions table
        html.Div(className="panel col-12", children=[
            html.Div("POSITIONS", style=_LABEL),
            base_table(df_positions, id="portfolio-positions-tbl") if not df_positions.empty
            else html.Div("Aucune position — lancez le pipeline ou un Backtest",
                         style={"color":"#5a7080","fontSize":"12px","padding":"16px 0"}),
        ], style=_CARD),

    ], style={"paddingBottom":"30px"})