# dashboard/pages/idea_lab.py — cartes lisibles + formatage correct

from dash import html, get_app
import dash_bootstrap_components as dbc
import pandas as pd

_CARD  = {"backgroundColor":"#0f141b","border":"1px solid #1e2a38","borderRadius":"8px","padding":"16px","marginBottom":"14px"}
_LABEL = {"fontSize":"10px","color":"#7eb8d8","textTransform":"uppercase","letterSpacing":".08em","marginBottom":"10px","fontWeight":"600"}
_H1    = {"fontSize":"11px","color":"#7eb8d8","textTransform":"uppercase","letterSpacing":".1em","marginBottom":"18px","fontWeight":"600"}


def _idea_card(idea, side):
    color  = "#4ade80" if side=="LONG" else "#f87171"
    conv   = idea.get("conviction","—")
    conv_c = "#4a9eff" if conv=="HIGH" else "#f0a500" if conv=="MEDIUM" else "#7090a8"
    score  = float(idea.get("score",0))
    m12    = idea.get("mom_12m")
    vol    = idea.get("vol_63d")
    pe     = idea.get("pe")
    roe    = idea.get("roe")

    return html.Div([
        html.Div([
            html.Span(idea.get("ticker",""), style={"fontSize":"14px","fontWeight":"700","color":"#e8f2ff","marginRight":"10px"}),
            html.Span(side, style={"fontSize":"10px","fontWeight":"700","color":color,
                "backgroundColor":f"rgba({'63,222,128' if side=='LONG' else '248,113,113'},.12)",
                "border":f"1px solid rgba({'63,222,128' if side=='LONG' else '248,113,113'},.3)",
                "borderRadius":"4px","padding":"2px 8px"}),
            html.Span(f" {conv}", style={"fontSize":"10px","color":conv_c,"marginLeft":"8px"}),
            html.Span(f"{score:.0f}/100", style={"fontSize":"11px","color":"#5a7080","marginLeft":"auto","fontVariantNumeric":"tabular-nums"}),
        ], style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
        html.Div([html.Div(style={"height":"3px","borderRadius":"2px","backgroundColor":color,"width":f"{int(score)}%"})],
                 style={"backgroundColor":"#1a2436","borderRadius":"2px","height":"3px","marginBottom":"8px"}),
        html.Div(idea.get("name",""), style={"fontSize":"11px","color":"#7090a8","marginBottom":"8px"}),
        html.Div([
            html.Div([
                html.Div("Mom 12M", style={"fontSize":"9px","color":"#5a7080","textTransform":"uppercase"}),
                html.Div(f"{m12*100:+.1f}%" if m12 is not None else "—",
                         style={"fontSize":"12px","fontWeight":"600","color":"#4ade80" if (m12 or 0)>0 else "#f87171"}),
            ], style={"flex":"1","textAlign":"center"}),
            html.Div([
                html.Div("Vol 63d", style={"fontSize":"9px","color":"#5a7080","textTransform":"uppercase"}),
                html.Div(f"{vol*100:.1f}%" if vol is not None else "—",
                         style={"fontSize":"12px","fontWeight":"600","color":"#94b8cc"}),
            ], style={"flex":"1","textAlign":"center"}),
            html.Div([
                html.Div("P/E", style={"fontSize":"9px","color":"#5a7080","textTransform":"uppercase"}),
                html.Div(f"{pe:.1f}x" if pe else "—",
                         style={"fontSize":"12px","fontWeight":"600","color":"#94b8cc"}),
            ], style={"flex":"1","textAlign":"center"}),
            html.Div([
                html.Div("ROE", style={"fontSize":"9px","color":"#5a7080","textTransform":"uppercase"}),
                html.Div(f"{roe*100:.1f}%" if roe else "—",
                         style={"fontSize":"12px","fontWeight":"600","color":"#94b8cc"}),
            ], style={"flex":"1","textAlign":"center"}),
        ], style={"display":"flex","gap":"4px","backgroundColor":"#0a0d12","borderRadius":"6px","padding":"8px","marginBottom":"8px"}),
        html.Div(idea.get("thesis",""), style={"fontSize":"11px","color":"#8aadcc","lineHeight":"1.5"}),
    ], style={**_CARD,"padding":"14px 16px","marginBottom":"10px"})


def layout():
    app = get_app()
    dp  = app.data_provider

    try:
        df = dp.get_trade_ideas()
        if df is None or not hasattr(df, 'empty') or df.empty:
            df = pd.DataFrame()
    except Exception:
        df = pd.DataFrame()

    longs  = df[df["side"]=="LONG"].head(5)  if not df.empty and "side" in df.columns else pd.DataFrame()
    shorts = df[df["side"]=="SHORT"].head(5) if not df.empty and "side" in df.columns else pd.DataFrame()
    n_long  = len(df[df["side"]=="LONG"])  if not df.empty and "side" in df.columns else 0
    n_short = len(df[df["side"]=="SHORT"]) if not df.empty and "side" in df.columns else 0
    n_high  = len(df[df["conviction"]=="HIGH"]) if not df.empty and "conviction" in df.columns else 0

    kpis = dbc.Row([
        dbc.Col(html.Div([html.Div("LONG IDEAS",style=_LABEL),html.Div(str(n_long),style={"fontSize":"26px","fontWeight":"700","color":"#4ade80"})],style={**_CARD,"padding":"14px 18px"}),width=3),
        dbc.Col(html.Div([html.Div("SHORT IDEAS",style=_LABEL),html.Div(str(n_short),style={"fontSize":"26px","fontWeight":"700","color":"#f87171"})],style={**_CARD,"padding":"14px 18px"}),width=3),
        dbc.Col(html.Div([html.Div("HIGH CONVICTION",style=_LABEL),html.Div(str(n_high),style={"fontSize":"26px","fontWeight":"700","color":"#4a9eff"})],style={**_CARD,"padding":"14px 18px"}),width=3),
        dbc.Col(html.Div([html.Div("MARKET REGIME",style=_LABEL),html.Div("Neutral",style={"fontSize":"26px","fontWeight":"700","color":"#f0a500"})],style={**_CARD,"padding":"14px 18px"}),width=3),
    ], className="g-3", style={"marginBottom":"14px"})

    long_list  = [_idea_card(r.to_dict(),"LONG")  for _,r in longs.iterrows()]
    short_list = [_idea_card(r.to_dict(),"SHORT") for _,r in shorts.iterrows()]

    no_long  = [html.Div("Aucune idée LONG",  style={"color":"#5a7080","fontSize":"12px","padding":"20px 0"})]
    no_short = [html.Div("Aucune idée SHORT — momentum positif généralisé", style={"color":"#5a7080","fontSize":"12px","padding":"20px 0"})]

    cols = dbc.Row([
        dbc.Col([html.Div("TOP LONG CANDIDATES", style={**_LABEL,"color":"#4ade80"})] + (long_list or no_long), width=6),
        dbc.Col([html.Div("TOP SHORT CANDIDATES", style={**_LABEL,"color":"#f87171"})] + (short_list or no_short), width=6),
    ], className="g-3")

    # Table complète formatée
    full_table = html.Div()
    if not df.empty:
        df_d = df[["ticker","name","side","score","conviction","mom_12m","vol_63d","pe","roe"]].copy()
        for col in ["ticker","name","side","conviction"]: df_d[col] = df_d[col].fillna("—")
        df_d["score"]   = df_d["score"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        df_d["mom_12m"] = df_d["mom_12m"].apply(lambda x: f"{x*100:+.1f}%" if pd.notna(x) else "—")
        df_d["vol_63d"] = df_d["vol_63d"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—")
        df_d["pe"]      = df_d["pe"].apply(lambda x: f"{x:.1f}x" if pd.notna(x) else "—")
        df_d["roe"]     = df_d["roe"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—")
        from dashboard.components.tables import base_table
        full_table = html.Div([
            html.Div("TOUTES LES IDÉES", style={**_LABEL,"marginTop":"8px"}),
            base_table(df_d, id="ideas-all-tbl", filter_row=True),
        ], style=_CARD)

    return html.Div([
        html.Div("Idea Lab", style=_H1),
        kpis, cols,
        html.Div(style={"height":"14px"}),
        full_table,
    ], style={"paddingBottom":"30px"})