# dashboard/callbacks/ai_callbacks.py — get_risk_metrics() appelé en dict safe

import json
from datetime import datetime
from dash import Input, Output, State, html, ALL, ctx
from ai.hypothesis_generator import HypothesisGenerator


def register_ai_callbacks(app):
    gen = HypothesisGenerator()

    @app.callback(
        Output("ai-output", "children"),
        Output("ai-history-store", "data"),
        Input("ai-submit-btn", "n_clicks"),
        Input({"type":"ai-quick","index":ALL}, "n_clicks"),
        State("ai-mode-dd",       "value"),
        State("ai-ticker-a",      "value"),
        State("ai-ticker-b",      "value"),
        State("ai-context-input", "value"),
        State("ai-history-store", "data"),
        prevent_initial_call=True,
    )
    def run_ai(n_submit, n_quick, mode, ticker_a, ticker_b, context, history):
        dp = app.data_provider

        quick_prompts = [
            "What is the current macro risk for this stock?",
            "Compare valuation vs sector peers",
            "Generate a bear case thesis",
            "What would trigger a change in direction?",
        ]
        triggered = ctx.triggered_id
        if isinstance(triggered, dict) and triggered.get("type") == "ai-quick":
            context = quick_prompts[triggered["index"]]

        if not ticker_a:
            return _msg("Select a ticker to analyse."), history

        from config.universe import TICKER_NAMES
        ticker_name = TICKER_NAMES.get(ticker_a, ticker_a)

        # Fondamentaux
        try:
            _, df_fund = dp.get_company_data(ticker_a)
            fund_dict = dict(zip(df_fund["metric"], df_fund["value"])) if not df_fund.empty else {}
        except Exception:
            fund_dict = {}

        # Scores facteurs
        try:
            df_factor = dp.get_factor_data()
            row = df_factor[df_factor["ticker"] == ticker_a]
            score_dict = row.to_dict("records")[0] if not row.empty else {}
        except Exception:
            score_dict = {}

        # Appel IA
        if mode == "hypothesis":
            result = gen.generate_hypothesis(ticker_a, ticker_name, fund_dict, score_dict, context or "")
            output = _render_hypothesis(result)

        elif mode == "pair" and ticker_b:
            ticker_b_name = TICKER_NAMES.get(ticker_b, ticker_b)
            try:
                _, df_b = dp.get_company_data(ticker_b)
                fund_b = dict(zip(df_b["metric"], df_b["value"])) if not df_b.empty else {}
            except Exception:
                fund_b = {}
            result = gen.compare_pair(ticker_a, ticker_b, fund_dict, fund_b)
            output = _render_text(result, f"Pair Trade: Long {ticker_a} / Short {ticker_b}")

        elif mode == "portfolio":
            try:
                kpis = dp.get_portfolio_kpis()
                # get_risk_metrics retourne un tuple → on extrait var et cvar
                risk_tuple = dp.get_risk_metrics()
                var_val  = risk_tuple[3] if isinstance(risk_tuple, tuple) and len(risk_tuple)>=5 else 0
                cvar_val = risk_tuple[4] if isinstance(risk_tuple, tuple) and len(risk_tuple)>=5 else 0
                risk_summary = {"var_95": float(var_val), "cvar_95": float(cvar_val)}
            except Exception:
                kpis, risk_summary = {}, {}
            result = gen.analyse_portfolio(kpis, risk_summary)
            output = _render_text(result, "Portfolio Commentary")

        else:
            ctx_str = f"Analysing: {ticker_a} ({ticker_name})\nFundamentals: {json.dumps(fund_dict, indent=2)}"
            result  = gen.free_analysis(context or "Provide a comprehensive analysis.", ctx_str)
            output  = _render_text(result, "Grok Analysis")

        entry   = {"timestamp": datetime.now().strftime("%H:%M:%S"),
                   "mode": mode, "ticker": ticker_a}
        history = ([entry] + (history or []))[:20]
        return output, history

    @app.callback(
        Output("ai-history-output", "children"),
        Input("ai-history-store", "data"),
    )
    def render_history(history):
        if not history:
            return html.Div("No analysis run yet.", style={"color":"#445566","fontSize":"11px"})
        return html.Div([
            html.Div([
                html.Span(h["timestamp"], style={"color":"#4a9eff","fontSize":"10px","marginRight":"8px"}),
                html.Span(h["mode"].upper(), style={"color":"#f0a500","fontSize":"10px","marginRight":"8px"}),
                html.Span(h["ticker"], style={"color":"#c0ccd8","fontSize":"10px","fontWeight":"500"}),
            ], style={"padding":"4px 0","borderBottom":"1px solid #1e2a38"})
            for h in history
        ])


def _msg(text):
    return html.Div(text, style={"color":"#445566","fontSize":"12px"})

def _render_text(text, title):
    return html.Div([
        html.Div(title, style={"fontSize":"11px","color":"#4a9eff","fontWeight":"600",
                               "marginBottom":"10px","textTransform":"uppercase","letterSpacing":"0.06em"}),
        html.Pre(text, style={"whiteSpace":"pre-wrap","fontSize":"12px","color":"#c0ccd8","lineHeight":"1.7"}),
    ])

def _render_hypothesis(h):
    if not isinstance(h, dict): return _render_text(str(h), "Analysis")
    direction = h.get("direction",""); conv = h.get("conviction","")
    dir_color = "#3fb950" if direction=="LONG" else "#f85149" if direction=="SHORT" else "#8899aa"
    conv_color= "#4a9eff" if conv=="HIGH" else "#f0a500" if conv=="MEDIUM" else "#8899aa"
    return html.Div([
        html.Div(style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"12px"}, children=[
            html.Div(h.get("ticker",""), style={"fontSize":"18px","fontWeight":"500","color":"#e2e8f0"}),
            html.Div(h.get("name",""),   style={"fontSize":"12px","color":"#8899aa"}),
            html.Span(direction, style={"background":"rgba(63,185,80,.15)" if direction=="LONG" else "rgba(248,81,73,.15)",
                                        "color":dir_color,"padding":"2px 8px","borderRadius":"4px","fontSize":"11px","fontWeight":"600"}),
            html.Span(f"Conviction: {conv}", style={"color":conv_color,"fontSize":"11px"}),
            html.Span(h.get("time_horizon",""), style={"color":"#445566","fontSize":"11px","marginLeft":"auto"}),
        ]),
        html.Div("Investment Thesis", style={"fontSize":"10px","color":"#445566","textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"4px"}),
        html.Div(h.get("thesis",""), style={"fontSize":"12px","color":"#c0ccd8","lineHeight":"1.7","marginBottom":"12px",
                                            "padding":"8px 10px","background":"#141d29","borderRadius":"4px","borderLeft":"2px solid #4a9eff"}),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"12px"}, children=[
            html.Div([
                html.Div("Catalysts", style={"fontSize":"10px","color":"#3fb950","textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"6px"}),
                html.Ul([html.Li(c, style={"fontSize":"11px","color":"#c0ccd8","marginBottom":"3px"}) for c in h.get("catalysts",[])], style={"paddingLeft":"14px"}),
            ]),
            html.Div([
                html.Div("Risks", style={"fontSize":"10px","color":"#f85149","textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"6px"}),
                html.Ul([html.Li(r, style={"fontSize":"11px","color":"#c0ccd8","marginBottom":"3px"}) for r in h.get("risks",[])], style={"paddingLeft":"14px"}),
            ]),
        ]),
        html.Div(style={"marginTop":"12px","padding":"8px 10px","background":"#141d29","borderRadius":"4px"}, children=[
            html.Div("Price Target Rationale", style={"fontSize":"10px","color":"#445566","textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"4px"}),
            html.Div(h.get("price_target_rationale",""), style={"fontSize":"11px","color":"#8899aa","lineHeight":"1.6"}),
        ]),
    ])