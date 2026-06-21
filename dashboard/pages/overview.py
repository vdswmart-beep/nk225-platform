# dashboard/pages/overview.py — FIXED: weights.values() bug

from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components.charts import line_chart, empty_fig

_CARD  = {"backgroundColor":"#0f141b","border":"1px solid #1e2a38","borderRadius":"8px","padding":"16px","marginBottom":"14px"}
_LABEL = {"fontSize":"10px","color":"#7eb8d8","textTransform":"uppercase","letterSpacing":".08em","marginBottom":"8px","fontWeight":"600"}
_H1    = {"fontSize":"11px","color":"#7eb8d8","textTransform":"uppercase","letterSpacing":".1em","marginBottom":"18px","fontWeight":"600"}

def _kpi(label, value, color="#4a9eff", sub=None):
    return html.Div([
        html.Div(label, style=_LABEL),
        html.Div(str(value), style={"fontSize":"26px","fontWeight":"700","color":color,"fontVariantNumeric":"tabular-nums"}),
        html.Div(sub, style={"fontSize":"11px","color":"#7090a8","marginTop":"4px"}) if sub else None,
    ], style={**_CARD,"padding":"14px 18px"})

def layout(dp=None):
    last_nav="—"; n_longs="—"; n_shorts="—"; n_tickers=0
    equity_fig = empty_fig(height=280, message="Lancez le pipeline ou un Backtest pour afficher la NAV")

    if dp is not None:
        n_tickers = len(dp.tickers)
        try:
            nav_df, weights = dp.get_portfolio()

            # Normaliser weights en dict (peut être DataFrame ou dict)
            if hasattr(weights, "to_dict"):
                if "ticker" in weights.columns and "weight" in weights.columns:
                    w = dict(zip(weights["ticker"], weights["weight"]))
                else:
                    w = {}
            elif isinstance(weights, dict):
                w = weights
            else:
                w = {}

            if nav_df is not None and not nav_df.empty and "nav" in nav_df.columns:
                last_val = float(nav_df["nav"].iloc[-1])
                last_nav = f"¥{last_val/1e6:.1f}M"
                # FIX: itération sur dict w, pas sur weights.values()
                n_longs  = str(sum(1 for v in w.values() if v > 0.001))
                n_shorts = str(sum(1 for v in w.values() if v < -0.001))
                equity_fig = line_chart(nav_df, "date", "nav",
                    title="NAV — Equity Curve (Equal Weight, base ¥100M)",
                    color="#4a9eff", height=280)
        except Exception as e:
            equity_fig = empty_fig(height=280, message=f"Erreur : {e}")

    tickers  = dp.tickers if dp and hasattr(dp, "tickers") else []
    tick_str = "   ".join(tickers[:15]) + ("  …" if len(tickers)>15 else "")

    return html.Div([
        html.Div("Overview", style=_H1),
        dbc.Row([
            dbc.Col(_kpi("NAV",         last_nav, "#4a9eff", sub="Base ¥100M · Equal weight"), width=3),
            dbc.Col(_kpi("Long Ideas",  n_longs,  "#4ade80"), width=3),
            dbc.Col(_kpi("Short Ideas", n_shorts, "#f87171"), width=3),
            dbc.Col(_kpi("Tickers",     str(n_tickers), "#f0a500", sub="Univers actif"), width=3),
        ], className="g-3", style={"marginBottom":"14px"}),
        html.Div([
            html.Div("EQUITY CURVE", style=_LABEL),
            dcc.Graph(figure=equity_fig, config={"displayModeBar":False}, style={"height":"280px"}),
        ], style=_CARD),
        html.Div([
            html.Div("UNIVERS D'INVESTISSEMENT", style=_LABEL),
            html.Div(tick_str, style={"fontSize":"12px","color":"#94b8cc",
                "fontFamily":"JetBrains Mono, monospace","lineHeight":"2.0"}),
        ], style=_CARD),
        dbc.Row([
            dbc.Col(html.A("📈 Backtest →", href="/backtest", style={"color":"#4a9eff","fontSize":"12px","textDecoration":"none","backgroundColor":"#111827","border":"1px solid #1e2a38","borderRadius":"6px","padding":"9px 16px","display":"block","textAlign":"center","fontWeight":"500"}), width=3),
            dbc.Col(html.A("💡 Idea Lab →", href="/ideas",   style={"color":"#4ade80","fontSize":"12px","textDecoration":"none","backgroundColor":"#111827","border":"1px solid #1e2a38","borderRadius":"6px","padding":"9px 16px","display":"block","textAlign":"center","fontWeight":"500"}), width=3),
            dbc.Col(html.A("🤖 AI Lab →",   href="/ai",      style={"color":"#c084fc","fontSize":"12px","textDecoration":"none","backgroundColor":"#111827","border":"1px solid #1e2a38","borderRadius":"6px","padding":"9px 16px","display":"block","textAlign":"center","fontWeight":"500"}), width=3),
            dbc.Col(html.A("⇄ Exécution →", href="/execution",style={"color":"#f0a500","fontSize":"12px","textDecoration":"none","backgroundColor":"#111827","border":"1px solid #1e2a38","borderRadius":"6px","padding":"9px 16px","display":"block","textAlign":"center","fontWeight":"500"}), width=3),
        ], className="g-3"),
    ], style={"paddingBottom":"30px"})