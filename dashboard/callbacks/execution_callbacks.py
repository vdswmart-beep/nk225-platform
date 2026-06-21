# dashboard/callbacks/execution_callbacks.py — P3-C: Callbacks Execution Lab

from __future__ import annotations
import json
import logging
import tempfile
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dash import Input, Output, State, callback, no_update, html, dash_table
from dash.exceptions import PreventUpdate

logger = logging.getLogger("ExecutionCallbacks")

_BG    = "#0f141b"
_BG2   = "#0a0d12"
_BORDER= "#1e2a38"
_GREEN = "#3fb950"
_RED   = "#f85149"
_BLUE  = "#4a9eff"
_TEXT  = "#c0ccd8"
_MUTED = "#8899aa"
_FONT  = "Inter, system-ui, sans-serif"

_TABLE_STYLE = dict(
    style_table  = {"overflowX": "auto", "border": "none"},
    style_header = {"backgroundColor": _BG2, "color": "#445566",
                    "fontWeight": "500", "fontSize": "10px",
                    "textTransform": "uppercase", "letterSpacing": ".06em",
                    "border": "none", "borderBottom": f"1px solid {_BORDER}",
                    "fontFamily": _FONT, "padding": "6px 10px"},
    style_cell   = {"backgroundColor": _BG, "color": _TEXT, "fontSize": "11px",
                    "border": "none", "borderBottom": f"1px solid {_BG2}",
                    "padding": "6px 10px", "fontFamily": _FONT},
)


def _colored_span(text, color):
    return html.Span(text, style={"color": color, "fontWeight": "600"})


def _empty_table(msg="Aucune donnée"):
    return html.Div(msg, style={"color": _MUTED, "fontSize": "11px", "padding": "8px 0"})


def register_execution_callbacks(app, dp, exec_engine=None):
    """
    Enregistre les callbacks de l'Execution Lab.

    Args:
        app:         Instance Dash
        dp:          DashboardDataProvider
        exec_engine: Instance PaperTradingEngine ou IBKRExecutionEngine
                     (None = paper trading par défaut)
    """
    # Engine paper par défaut si non fourni
    if exec_engine is None:
        from execution.execution_engine import PaperTradingEngine
        exec_engine = PaperTradingEngine(commission_bps=3.0, slippage_bps=5.0)

    # Cache fills en mémoire (complété par dcc.Store)
    _fills_cache: list = []

    # ── Prévisualisation ordre ────────────────────────────────────

    @app.callback(
        Output("exec-order-preview", "children"),
        Input("exec-ticker",      "value"),
        Input("exec-action",      "value"),
        Input("exec-order-type",  "value"),
        Input("exec-qty",         "value"),
        Input("exec-limit-price", "value"),
    )
    def preview_order(ticker, action, order_type, qty, limit_price):
        if not ticker or not qty:
            return "Sélectionnez un ticker et une quantité pour prévisualiser l'ordre."

        qty = int(qty) if qty else 0
        action_color = _GREEN if action == "BUY" else _RED

        # Prix de référence
        try:
            prices = dp.get_live_prices() if hasattr(dp, "get_live_prices") else {}
            ref    = prices.get(ticker, 0)
        except Exception:
            ref = 0

        est_notional = qty * (limit_price or ref or 0)

        parts = [
            _colored_span(f"{action} ", action_color),
            html.Span(f"{qty:,} × "),
            html.Span(f"{ticker} ", style={"color": _BLUE, "fontWeight": "600"}),
            html.Span("@ "),
        ]
        if order_type == "LIMIT" and limit_price:
            parts.append(html.Span(f"LIMIT ¥{float(limit_price):,.0f}",
                                   style={"color": "#f0a500", "fontWeight": "600"}))
        else:
            parts.append(html.Span("MARKET", style={"color": _MUTED}))

        if est_notional > 0:
            parts.append(html.Span(
                f" | Notionnel estimé : ¥{est_notional:,.0f}",
                style={"color": _MUTED, "marginLeft": "8px"},
            ))

        return html.Div(parts)

    # ── Valider ordre ─────────────────────────────────────────────

    @app.callback(
        Output("exec-submit-status",  "children"),
        Output("exec-fills-store",    "data"),
        Input("exec-submit-btn",      "n_clicks"),
        State("exec-ticker",          "value"),
        State("exec-action",          "value"),
        State("exec-order-type",      "value"),
        State("exec-qty",             "value"),
        State("exec-limit-price",     "value"),
        State("exec-fills-store",     "data"),
        prevent_initial_call=True,
    )
    def submit_order(n_clicks, ticker, action, order_type, qty,
                     limit_price, fills_data):
        if not n_clicks or not ticker or not qty:
            raise PreventUpdate

        from execution.execution_engine import Order

        order = Order(
            ticker      = ticker,
            action      = action,
            qty         = int(qty),
            order_type  = order_type,
            limit_price = float(limit_price) if limit_price else None,
            side        = "LONG" if action in ("BUY", "COVER") else "SHORT",
        )

        # Prix de référence (depuis dp ou fallback)
        try:
            prices = dp.get_current_prices() if hasattr(dp, "get_current_prices") else {}
            ref    = float(prices.get(ticker, 1000))
        except Exception:
            ref = 1000.0

        try:
            fill = exec_engine.execute_order(order, ref)

            if fill is None:
                status = html.Div(
                    [html.Span("✖ ", style={"color": _RED}),
                     f"Ordre rejeté : {ticker} ({order_type})"],
                    style={"color": _RED, "fontSize": "12px"},
                )
                return status, fills_data

            # Mise à jour cache
            fill_dict = {
                "order_id":   fill.order_id,
                "time":       fill.filled_at,
                "ticker":     fill.ticker,
                "action":     fill.action,
                "qty":        fill.qty,
                "fill_price": fill.fill_price,
                "notional":   round(fill.qty * fill.fill_price, 0),
                "commission": fill.commission,
                "slippage":   fill.slippage,
                "status":     fill.status,
            }
            current = json.loads(fills_data) if fills_data else []
            current.append(fill_dict)

            # Log dans track record
            try:
                from reporting.track_record import TrackRecord
                tr = TrackRecord(auto_save=False)
                tr.log_trade(
                    ticker     = fill.ticker,
                    action     = fill.action,
                    qty        = fill.qty,
                    price      = fill.fill_price,
                    commission = fill.commission,
                    slippage   = fill.slippage,
                )
            except Exception as e:
                logger.debug(f"Track record log skipped: {e}")

            status = html.Div([
                html.Span("✔ Exécuté : ", style={"color": _GREEN}),
                html.Span(f"{fill.action} {fill.qty:,} × {fill.ticker} "
                          f"@ ¥{fill.fill_price:,.0f} ",
                          style={"color": _TEXT, "fontWeight": "600"}),
                html.Span(f"| Commission ¥{fill.commission:.0f} "
                          f"| Slippage ¥{fill.slippage:.0f}",
                          style={"color": _MUTED}),
            ], style={"fontSize": "12px"})

            return status, json.dumps(current)

        except Exception as e:
            logger.error(f"submit_order error: {e}", exc_info=True)
            return html.Div(f"⚠ Erreur : {e}",
                            style={"color": _RED, "fontSize": "12px"}), fills_data

    # ── Blotter (affichage fills) ──────────────────────────────────

    @app.callback(
        Output("exec-blotter-table",   "children"),
        Output("exec-blotter-summary", "children"),
        Input("exec-fills-store",      "data"),
        Input("exec-refresh-btn",      "n_clicks"),
    )
    def update_blotter(fills_data, _refresh):
        fills = json.loads(fills_data) if fills_data else []
        if not fills:
            return _empty_table("Aucun ordre exécuté"), ""

        df = pd.DataFrame(fills)
        df = df.sort_values("time", ascending=False)

        total_notional = df["notional"].sum()
        total_cost     = df["commission"].sum() + df["slippage"].sum()
        n_fills        = len(df)

        table = dash_table.DataTable(
            columns=[{"name": c.upper().replace("_", " "), "id": c}
                     for c in df.columns],
            data=df.round(2).to_dict("records"),
            page_size=10,
            sort_action="native",
            **_TABLE_STYLE,
            style_data_conditional=[
                {"if": {"filter_query": "{action} = 'BUY'",  "column_id": "action"},
                 "color": _GREEN},
                {"if": {"filter_query": "{action} = 'SELL'", "column_id": "action"},
                 "color": _RED},
            ],
        )

        summary = (
            f"{n_fills} fills | "
            f"Notionnel total ¥{total_notional:,.0f} | "
            f"Coûts totaux ¥{total_cost:,.0f}"
        )
        return table, summary

    # ── Positions ─────────────────────────────────────────────────

    @app.callback(
        Output("exec-positions-table", "children"),
        Input("exec-refresh-btn",      "n_clicks"),
        Input("exec-fills-store",      "data"),
    )
    def update_positions(_refresh, fills_data):
        positions = exec_engine.get_positions()
        if not positions:
            return _empty_table("Aucune position ouverte")

        rows = [{"ticker": t, "qty": q,
                 "side": "LONG" if q > 0 else "SHORT"}
                for t, q in positions.items()]
        df = pd.DataFrame(rows)

        return dash_table.DataTable(
            columns=[{"name": c.upper(), "id": c} for c in df.columns],
            data=df.to_dict("records"),
            **_TABLE_STYLE,
            style_data_conditional=[
                {"if": {"filter_query": "{side} = 'LONG'",  "column_id": "side"},
                 "color": _GREEN},
                {"if": {"filter_query": "{side} = 'SHORT'", "column_id": "side"},
                 "color": _RED},
            ],
        )

    # ── Delta pipeline → cibles ───────────────────────────────────

    @app.callback(
        Output("exec-delta-table",  "children"),
        Input("exec-refresh-btn",   "n_clicks"),
    )
    def update_deltas(_refresh):
        try:
            target_weights = getattr(dp, "target_weights", {})
            if not target_weights:
                return _empty_table("Aucun poids cible — lancez le pipeline d'abord")

            current_pos = exec_engine.get_positions()
            rows = []
            for ticker, target_w in target_weights.items():
                current_qty = current_pos.get(ticker, 0)
                rows.append({
                    "ticker":       ticker,
                    "target_w":    f"{target_w:.2%}",
                    "current_qty": current_qty,
                    "action":      "BUY" if target_w > 0 else "SELL",
                })

            if not rows:
                return _empty_table("Pas de deltas calculés")

            df = pd.DataFrame(rows)
            return dash_table.DataTable(
                columns=[{"name": c.upper().replace("_", " "), "id": c}
                         for c in df.columns],
                data=df.to_dict("records"),
                **_TABLE_STYLE,
                style_data_conditional=[
                    {"if": {"filter_query": "{action} = 'BUY'",  "column_id": "action"},
                     "color": _GREEN},
                    {"if": {"filter_query": "{action} = 'SELL'", "column_id": "action"},
                     "color": _RED},
                ],
            )
        except Exception as e:
            return _empty_table(f"Erreur deltas : {e}")

    # ── Exécuter tous les deltas ──────────────────────────────────

    @app.callback(
        Output("exec-delta-status", "children"),
        Input("exec-execute-all-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def execute_all_deltas(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        try:
            target_weights = getattr(dp, "target_weights", {})
            if not target_weights:
                return "⚠ Aucun poids cible disponible"

            from execution.execution_engine import Order
            prices = getattr(dp, "_last_prices", {})
            orders = []
            for ticker, w in target_weights.items():
                ref = float(prices.get(ticker, 1000))
                nav = 100_000_000
                notional = abs(w) * nav
                qty = max(1, int(notional / ref))
                orders.append(Order(
                    ticker     = ticker,
                    action     = "BUY" if w > 0 else "SELL",
                    qty        = qty,
                    order_type = "MARKET",
                    side       = "LONG" if w > 0 else "SHORT",
                ))

            result = exec_engine.execute_portfolio(orders, prices)
            return (
                f"✔ {len(result.fills)} ordres exécutés | "
                f"{len(result.rejected)} rejetés | "
                f"Coût total ¥{result.total_cost:,.0f}"
            )
        except Exception as e:
            logger.error(f"execute_all_deltas: {e}")
            return f"⚠ Erreur : {e}"

    # ── Export blotter Excel ──────────────────────────────────────

    @app.callback(
        Output("exec-download", "data"),
        Input("exec-export-btn", "n_clicks"),
        State("exec-fills-store", "data"),
        prevent_initial_call=True,
    )
    def export_blotter(n_clicks, fills_data):
        if not n_clicks or not fills_data:
            raise PreventUpdate
        try:
            fills = json.loads(fills_data)
            df    = pd.DataFrame(fills)

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                tmp_path = tmp.name

            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Blotter", index=False)

            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)

            from dash import dcc as _dcc
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            return _dcc.send_bytes(data, f"blotter_{date_str}.xlsx")
        except Exception as e:
            logger.error(f"export_blotter: {e}")
            raise PreventUpdate