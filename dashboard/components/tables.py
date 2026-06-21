# dashboard/components/tables.py

from dash import dash_table
import pandas as pd

_BG    = "#0f141b"
_BG2   = "#0a0d12"
_BORDER= "#1e2a38"
_HDR   = "#445566"
_CELL  = "#c0ccd8"
_FONT  = "Inter, system-ui, sans-serif"


def base_table(df: pd.DataFrame, id: str = "tbl", page_size: int = 20,
               sort: bool = True, filter_row: bool = False,
               col_widths: dict = None):
    if df is None or df.empty:
        return dash_table.DataTable(id=id)

    columns = []
    for c in df.columns:
        col = {"name": c, "id": c}
        if pd.api.types.is_float_dtype(df[c]):
            col["type"] = "numeric"
            col["format"] = {"specifier": ".4f"}
        columns.append(col)

    style_cell_conditional = []
    if col_widths:
        for col_id, width in col_widths.items():
            style_cell_conditional.append({
                "if": {"column_id": col_id},
                "width": width, "minWidth": width, "maxWidth": width,
            })

    return dash_table.DataTable(
        id=id,
        columns=columns,
        data=df.to_dict("records"),
        page_size=page_size,
        sort_action="native" if sort else "none",
        filter_action="native" if filter_row else "none",
        style_table={"overflowX": "auto", "border": "none"},
        style_header={
            "backgroundColor": _BG2,
            "color": _HDR,
            "fontWeight": "500",
            "fontSize": "10px",
            "textTransform": "uppercase",
            "letterSpacing": "0.06em",
            "border": "none",
            "borderBottom": f"1px solid {_BORDER}",
            "fontFamily": _FONT,
            "padding": "6px 10px",
        },
        style_cell={
            "backgroundColor": _BG,
            "color": _CELL,
            "fontSize": "11px",
            "border": "none",
            "borderBottom": f"1px solid {_BG2}",
            "padding": "6px 10px",
            "fontFamily": _FONT,
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data_conditional=[
            {"if": {"state": "active"}, "backgroundColor": "#141d29", "border": "none"},
            {"if": {"state": "selected"}, "backgroundColor": "#192334", "border": "none"},
            {"if": {"filter_query": "{side} = 'BUY' || {side} = 'LONG'", "column_id": "side"}, "color": "#3fb950"},
            {"if": {"filter_query": "{side} = 'SELL' || {side} = 'SHORT'", "column_id": "side"}, "color": "#f85149"},
            {"if": {"filter_query": "{conviction} = 'HIGH'", "column_id": "conviction"}, "color": "#4a9eff"},
            {"if": {"filter_query": "{conviction} = 'MEDIUM'", "column_id": "conviction"}, "color": "#f0a500"},
        ],
        css=[{"selector": ".dash-filter input", "rule": f"background: {_BG2}; color: {_CELL}; border: 1px solid {_BORDER}; font-size: 11px;"}],
    )
