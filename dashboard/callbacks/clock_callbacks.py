# dashboard/callbacks/clock_callbacks.py — ID corrigé: topbar-clock

from dash import Input, Output
from datetime import datetime


def register_clock_callbacks(app):

    @app.callback(
        Output("topbar-clock", "children"),   # ID exact du layout.py
        Input("clock-interval", "n_intervals"),
    )
    def update_clock(n):
        return datetime.now().strftime("%H:%M:%S JST")