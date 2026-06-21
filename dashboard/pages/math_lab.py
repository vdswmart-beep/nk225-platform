# dashboard/pages/math_lab.py

from dash import html, dcc, get_app
from dashboard.components.charts import bar_chart, scatter_chart, line_chart
from dashboard.components.tables import base_table
from dashboard.components.filters import dropdown, radio_pills
import pandas as pd


def layout():
    app = get_app()
    dp  = app.data_provider

    tickers      = dp.tickers
    ticker_opts  = tickers
    factor_opts  = ["mom_12m", "mom_6m", "roe", "pe", "vol_252d", "pb", "fcf_yield"]
    test_opts    = ["ADF (Stationarity)", "Jarque-Bera (Normality)", "T-Test (Mean=0)", "Bootstrap CI"]
    method_opts  = ["OLS Regression", "PCA", "Rolling Beta", "Correlation Matrix"]

    return html.Div([
        html.Div("Math Lab", className="section-title"),

        html.Div(className="grid", children=[

            # Controls
            html.Div(className="panel col-12", children=[
                html.Div(style={"display":"flex","gap":"16px","flexWrap":"wrap"}, children=[
                    html.Div(style={"flex":"1","minWidth":"160px"}, children=[
                        dropdown("math-ticker-a",  ticker_opts, value=tickers[0],  label="Ticker A", clearable=False),
                    ]),
                    html.Div(style={"flex":"1","minWidth":"160px"}, children=[
                        dropdown("math-ticker-b",  ticker_opts, value=tickers[1] if len(tickers)>1 else tickers[0], label="Ticker B", clearable=False),
                    ]),
                    html.Div(style={"flex":"1","minWidth":"160px"}, children=[
                        dropdown("math-factor",    factor_opts, value="mom_12m",   label="Factor",   clearable=False),
                    ]),
                    html.Div(style={"flex":"1","minWidth":"180px"}, children=[
                        dropdown("math-method",    method_opts, value=method_opts[0], label="Method", clearable=False),
                    ]),
                    html.Div(style={"flex":"1","minWidth":"160px"}, children=[
                        dropdown("math-test",      test_opts,   value=test_opts[0],  label="Statistical Test", clearable=False),
                    ]),
                    html.Div(style={"alignSelf":"flex-end","paddingBottom":"8px"}, children=[
                        html.Button("Run Analysis", id="math-run-btn",
                                    style={"background":"#192334","border":"1px solid #1e2a38",
                                           "color":"#4a9eff","padding":"7px 16px","borderRadius":"4px",
                                           "cursor":"pointer","fontSize":"12px","fontWeight":"500"}),
                    ]),
                ]),
            ]),

            # Output panels
            html.Div(className="panel col-8", id="math-chart-panel", children=[
                html.Div("Select parameters and click Run Analysis", className="section-title"),
                dcc.Loading(html.Div(id="math-chart-output"), type="dot", color="#4a9eff"),
            ]),

            html.Div(className="panel col-4", id="math-stats-panel", children=[
                html.Div("Statistical Test Results", className="section-title"),
                dcc.Loading(html.Div(id="math-stats-output"), type="dot", color="#4a9eff"),
            ]),

            # Correlation heatmap
            html.Div(className="panel col-12", children=[
                html.Div("Return Correlation Matrix", className="section-title"),
                dcc.Loading(html.Div(id="math-corr-output"), type="dot", color="#4a9eff"),
            ]),

            # PCA variance explained
            html.Div(className="panel col-6", children=[
                html.Div("PCA — Explained Variance", className="section-title"),
                dcc.Loading(html.Div(id="math-pca-output"), type="dot", color="#4a9eff"),
            ]),

            # Rolling beta
            html.Div(className="panel col-6", children=[
                html.Div("Rolling Beta (63d window)", className="section-title"),
                dcc.Loading(html.Div(id="math-beta-output"), type="dot", color="#4a9eff"),
            ]),
        ]),

        # Hidden store for pre-computed data
        dcc.Store(id="math-data-store"),
    ])
