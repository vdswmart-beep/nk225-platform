# dashboard/components/filters.py

from dash import dcc, html

_STYLE_DD = {
    "backgroundColor": "#0f141b",
    "color": "#c0ccd8",
    "border": "1px solid #1e2a38",
    "borderRadius": "4px",
    "fontSize": "12px",
    "marginBottom": "8px",
}


def dropdown(id: str, options, multi: bool = False,
             placeholder: str = "Select...", value=None,
             clearable: bool = True, label: str = None):
    opts = [{"label": str(o), "value": o} for o in options]
    dd = dcc.Dropdown(
        id=id,
        options=opts,
        multi=multi,
        placeholder=placeholder,
        value=value,
        clearable=clearable,
        style=_STYLE_DD,
    )
    if label:
        return html.Div([
            html.Div(label, style={"fontSize": "10px", "color": "#445566",
                                   "textTransform": "uppercase", "letterSpacing": "0.06em",
                                   "marginBottom": "4px"}),
            dd,
        ])
    return dd


def radio_pills(id: str, options: list, value=None):
    return dcc.RadioItems(
        id=id,
        options=[{"label": o, "value": o} for o in options],
        value=value or options[0],
        inline=True,
        inputStyle={"display": "none"},
        labelStyle={
            "display": "inline-block",
            "padding": "3px 10px",
            "marginRight": "4px",
            "borderRadius": "4px",
            "border": "1px solid #1e2a38",
            "cursor": "pointer",
            "fontSize": "11px",
            "color": "#8899aa",
        },
        style={"marginBottom": "10px"},
    )


def date_range(id: str, start: str, end: str):
    return dcc.DatePickerRange(
        id=id,
        start_date=start,
        end_date=end,
        display_format="YYYY-MM-DD",
        style={"fontSize": "11px"},
    )
