# dashboard/layout.py — FIXED: couleurs visibles, structure simple

from dash import html, dcc

# Couleurs visibles
_NAV_BG   = "#0d1117"
_NAV_TEXT = "#a0b8cc"   # texte nav visible
_NAV_SEC  = "#4a6070"   # section titles visibles
_ACCENT   = "#4a9eff"
_BORDER   = "#1e2a38"
_BG       = "#0a0d12"


def build_layout(dp=None):

    def nav_section(title):
        return html.Div(title, style={
            "fontSize": "9px", "fontWeight": "600",
            "color": _NAV_SEC,
            "textTransform": "uppercase", "letterSpacing": ".1em",
            "padding": "14px 12px 5px",
        })

    def nav_link(icon, label, href):
        return html.A([
            html.Span(icon, style={"marginRight": "8px", "fontSize": "13px"}),
            html.Span(label),
        ], href=href, style={
            "display": "flex", "alignItems": "center",
            "padding": "7px 12px",
            "color": _NAV_TEXT,
            "textDecoration": "none",
            "borderRadius": "5px",
            "marginBottom": "2px",
            "fontSize": "12px",
            "fontWeight": "400",
        })

    sidebar = html.Div([
        # Logo
        html.Div([
            html.Span("NK225", style={"fontSize": "15px", "fontWeight": "700",
                                      "color": _ACCENT}),
            html.Span(" Platform", style={"fontSize": "12px", "color": "#5a7080",
                                           "marginLeft": "4px"}),
        ], style={"padding": "18px 14px 16px",
                  "borderBottom": f"1px solid {_BORDER}",
                  "marginBottom": "8px"}),

        nav_section("ANALYSIS"),
        nav_link("▣", "Overview",     "/"),
        nav_link("⚗", "Research Lab", "/research"),
        nav_link("💡", "Idea Lab",     "/ideas"),
        nav_link("⊞", "Math Lab",     "/math"),
        nav_link("🤖", "AI Lab",       "/ai"),

        nav_section("BACKTEST"),
        nav_link("📈", "Backtest Lab", "/backtest"),

        nav_section("PORTFOLIO"),
        nav_link("◎", "Portfolio",    "/portfolio"),
        nav_link("⊘", "Risk Lab",     "/risk"),

        nav_section("EXECUTION"),
        nav_link("⇄", "Execution",    "/execution"),
        nav_link("▣", "Company",      "/company"),

        html.Div("NK225 Platform v2.0", style={
            "fontSize": "9px", "color": "#2e3d4f",
            "padding": "16px 14px", "marginTop": "auto",
            "borderTop": f"1px solid {_BORDER}",
        }),
    ], style={
        "width": "210px", "minWidth": "210px",
        "backgroundColor": _NAV_BG,
        "borderRight": f"1px solid {_BORDER}",
        "position": "fixed",
        "top": "0", "left": "0",
        "height": "100vh",
        "display": "flex", "flexDirection": "column",
        "overflowY": "auto",
        "zIndex": "100",
    })

    topbar = html.Div([
        html.Div([
            html.Span("NK225 ", style={"fontSize": "11px", "color": "#5a7080",
                                       "textTransform": "uppercase", "letterSpacing": ".06em"}),
            html.Span("38,420", style={"fontSize": "13px", "fontWeight": "600",
                                        "color": "#c8d8e8", "marginRight": "20px"}),
            html.Span("USD/JPY ", style={"fontSize": "11px", "color": "#5a7080",
                                          "textTransform": "uppercase", "letterSpacing": ".06em"}),
            html.Span("157.34", style={"fontSize": "13px", "fontWeight": "600",
                                        "color": "#c8d8e8"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "4px"}),
        html.Div([
            html.Span("● LIVE", style={"fontSize": "10px", "fontWeight": "600",
                                        "color": "#3fb950", "marginRight": "16px"}),
            html.Span(id="topbar-clock",
                      style={"fontSize": "11px", "color": "#7090a8",
                             "fontVariantNumeric": "tabular-nums"}),
        ], style={"display": "flex", "alignItems": "center"}),
        dcc.Interval(id="clock-interval", interval=1000, n_intervals=0),
    ], style={
        "position": "fixed",
        "top": "0", "left": "210px", "right": "0",
        "height": "44px",
        "backgroundColor": "#08090f",
        "borderBottom": f"1px solid {_BORDER}",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "space-between",
        "padding": "0 24px",
        "zIndex": "99",
    })

    content = html.Div(
        id="page-content",
        style={
            "marginLeft": "210px",
            "marginTop":  "44px",
            "padding":    "20px 24px",
            "minHeight":  "calc(100vh - 44px)",
            "backgroundColor": _BG,
        },
    )

    return html.Div([
        sidebar,
        topbar,
        content,
        dcc.Location(id="url", refresh=False),
    ], style={
        "backgroundColor": _BG,
        "minHeight": "100vh",
        "fontFamily": "Inter, system-ui, sans-serif",
        "color": "#c8d8e8",
    })