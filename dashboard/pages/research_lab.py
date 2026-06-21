# dashboard/pages/research_lab.py

from dash import html, dcc, get_app
from dashboard.components.charts import bar_chart, line_chart
from dashboard.components.tables import base_table
from dashboard.components.filters import dropdown, radio_pills


def layout():
    app = get_app()
    dp = app.data_provider

    df_factor = dp.get_factor_data()
    df_ic     = dp.get_ic_series()

    sectors = ["All"] + (df_factor["name"].dropna().unique().tolist() if "name" in df_factor.columns else [])

    return html.Div([
        html.Div("Research Lab", className="section-title"),

        html.Div(className="grid", children=[

            # IC stats KPIs
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("IC Mean", className="kpi-label"),
                    html.Div(
                        f"{df_ic['ic'].mean():.3f}" if not df_ic.empty else "—",
                        className="kpi-value",
                    ),
                    html.Div("Spearman rank", className="kpi-sub kpi-neutral"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("IC IR", className="kpi-label"),
                    html.Div(
                        f"{df_ic['ic'].mean()/df_ic['ic'].std():.2f}" if (not df_ic.empty and df_ic['ic'].std()>0) else "—",
                        className="kpi-value",
                    ),
                    html.Div("IC / IC-Std", className="kpi-sub kpi-neutral"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("Hit Ratio", className="kpi-label"),
                    html.Div(
                        f"{(df_ic['ic']>0).mean()*100:.1f}%" if not df_ic.empty else "—",
                        className="kpi-value",
                    ),
                    html.Div("% positive IC months", className="kpi-sub kpi-neutral"),
                ])
            ]),
            html.Div(className="panel col-3", children=[
                html.Div(className="kpi", children=[
                    html.Div("Observations", className="kpi-label"),
                    html.Div(f"{len(df_ic)}", className="kpi-value"),
                    html.Div("Trading days", className="kpi-sub kpi-neutral"),
                ])
            ]),

            # IC series
            html.Div(className="panel col-12", children=[
                html.Div("Factor IC Series (Rolling Spearman)", className="section-title"),
                dcc.Graph(
                    figure=bar_chart(df_ic.tail(252), "date", "ic", color="diverging", height=180),
                    config={"displayModeBar": False},
                )
            ]),

            # Factor table
            html.Div(className="panel col-12", children=[
                html.Div("Latest Factor Scores", className="section-title"),
                base_table(df_factor, id="research-factor-tbl", filter_row=True),
            ]),
        ])
    ])
