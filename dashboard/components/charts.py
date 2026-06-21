# dashboard/components/charts.py — FIXED (BUG-01: fillcolor rgba invalide)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

_BG   = "#0f141b"
_BG2  = "#0a0d12"
_GRID = "rgba(255,255,255,0.04)"
_TEXT = "#8899aa"
_FONT = dict(family="Inter, system-ui, sans-serif", color=_TEXT, size=11)

PALETTE = ["#4a9eff", "#3fb950", "#f0a500", "#e066cc", "#60c4cc",
           "#f85149", "#d2a8ff", "#ffa657"]


# ── FIX BUG-01 ────────────────────────────────────────────────────────────────
def _hex_to_rgba(hex_color: str, alpha: float = 0.07) -> str:
    """
    Convertit une couleur hex (#rrggbb) en chaîne rgba() valide pour Plotly.
    Gère aussi les couleurs déjà en format rgba() — les retourne telles quelles.
    """
    if hex_color.startswith("rgba(") or hex_color.startswith("rgb("):
        return hex_color
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except (ValueError, IndexError):
        return f"rgba(74,158,255,{alpha})"   # fallback bleu accent
# ──────────────────────────────────────────────────────────────────────────────


def _base_layout(**kwargs):
    layout = dict(
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=_FONT,
        margin=dict(l=40, r=16, t=28, b=36),
        showlegend=False,
        xaxis=dict(gridcolor=_GRID, linecolor="#1e2a38",
                   tickfont=dict(size=10, color=_TEXT), zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor="#1e2a38",
                   tickfont=dict(size=10, color=_TEXT), zeroline=False),
    )
    layout.update(kwargs)
    return layout


def line_chart(df, x_col, y_col, title="", color="#4a9eff", height=200):
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(**_base_layout(height=height))
        return fig
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="lines",
        line=dict(color=color, width=1.5),
        fill="tozeroy",
        fillcolor=_hex_to_rgba(color, 0.07),          # FIX BUG-01
        hovertemplate="%{x}<br><b>%{y:.2f}</b><extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0, pad=dict(l=0))
    ))
    return fig


def multi_line_chart(df, x_col, y_cols, title="", height=200):
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(**_base_layout(height=height))
        return fig
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[col], name=col,
            mode="lines",
            line=dict(color=PALETTE[i % len(PALETTE)], width=1.5),
            hovertemplate=f"{col}: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(**_base_layout(
        height=height,
        showlegend=True,
        legend=dict(font=dict(size=10, color=_TEXT), bgcolor="rgba(0,0,0,0)",
                    orientation="h", y=1.08, x=0),
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
    ))
    return fig


def bar_chart(df, x_col, y_col, title="", color="#4a9eff", height=200):
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(**_base_layout(height=height))
        return fig
    colors = (
        [("#3fb950" if v >= 0 else "#f85149") for v in df[y_col]]
        if color == "diverging" else color
    )
    fig.add_trace(go.Bar(
        x=df[x_col], y=df[y_col],
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:.4f}</b><extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
        bargap=0.25,
    ))
    return fig


def hbar_chart(labels, values, title="", height=200):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=labels,
        orientation="h",
        marker=dict(color=PALETTE[:len(labels)], line=dict(width=0)),
        hovertemplate="%{y}: <b>%{x:.1f}%</b><extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
        xaxis=dict(gridcolor=_GRID, ticksuffix="%", tickfont=dict(size=10, color=_TEXT)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color=_TEXT)),
        bargap=0.3,
        margin=dict(l=80, r=16, t=28, b=28),
    ))
    return fig


def donut_chart(labels, values, title="", height=220):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=PALETTE[:len(labels)], line=dict(color=_BG2, width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_BG, font=_FONT,
        margin=dict(l=10, r=10, t=28, b=10),
        showlegend=True,
        legend=dict(font=dict(size=10, color=_TEXT), bgcolor="rgba(0,0,0,0)",
                    x=0.5, xanchor="center", y=-0.05, orientation="h"),
        title=dict(text=title, font=dict(size=11, color="#445566"),
                   x=0.5, xanchor="center"),
        height=height,
    )
    return fig


def scatter_chart(df, x_col, y_col, label_col=None, title="",
                  height=220, color="#4a9eff"):
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(**_base_layout(height=height))
        return fig
    text = df[label_col] if label_col and label_col in df.columns else None
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="markers+text" if text is not None else "markers",
        text=text,
        textposition="top center",
        textfont=dict(size=9, color=_TEXT),
        marker=dict(color=color, size=8, line=dict(width=0)),
        hovertemplate="%{x:.2f} / %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
    ))
    return fig


def correlation_heatmap(corr_df: "pd.DataFrame", title="Correlation Matrix",
                        height=340):
    """Heatmap pour la matrice de corrélation — utilisé par Math Lab."""
    fig = go.Figure(go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns.tolist(),
        y=corr_df.index.tolist(),
        colorscale=[
            [0.0,  "#f85149"],
            [0.5,  "#0f141b"],
            [1.0,  "#4a9eff"],
        ],
        zmin=-1, zmax=1,
        text=corr_df.round(2).values,
        texttemplate="%{text}",
        textfont=dict(size=9),
        hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>ρ = %{z:.3f}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickfont=dict(size=9, color=_TEXT),
            thickness=10,
            len=0.8,
        ),
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
        margin=dict(l=60, r=40, t=36, b=60),
    ))
    return fig


def area_fill_chart(df, x_col, y_col, title="", color="#f85149", height=180):
    """Utilisé pour le drawdown — zone négative en rouge."""
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(**_base_layout(height=height))
        return fig
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="lines",
        line=dict(color=color, width=1.2),
        fill="tozeroy",
        fillcolor=_hex_to_rgba(color, 0.12),           # FIX BUG-01
        hovertemplate="%{x}<br><b>%{y:.2%}</b><extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        height=height,
        title=dict(text=title, font=dict(size=11, color="#445566"), x=0),
        yaxis=dict(tickformat=".1%", gridcolor=_GRID,
                   tickfont=dict(size=10, color=_TEXT)),
    ))
    return fig


def empty_fig(height=200, message="Pas de données disponibles"):
    """Figure vide avec message — utilisée en fallback dans tous les callbacks."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=12, color=_TEXT),
    )
    fig.update_layout(**_base_layout(height=height))
    return fig