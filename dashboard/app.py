# dashboard/app.py — FIXED: assets_folder pointe vers dashboard/asset/

import os
import logging
import inspect
import dash
import dash_bootstrap_components as dbc
from dashboard.layout import build_layout
from dashboard.router  import register_router

logger = logging.getLogger("DashApp")

# Chemin absolu vers le dossier CSS (asset/, pas assets/)
_ASSET_DIR = os.path.join(os.path.dirname(__file__), "asset")


def _register(label, fn, app, dp):
    try:
        n = len(inspect.signature(fn).parameters)
        fn(app, dp) if n >= 2 else fn(app)
        logger.info(f"✓ {label}")
    except Exception as e:
        logger.warning(f"✗ {label}: {e}")


def build_dashboard(data_provider=None):
    app = dash.Dash(
        __name__,
        assets_folder=_ASSET_DIR,          # ← FIX: charge dashboard/asset/global.css
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        ],
        suppress_callback_exceptions=True,
        title="NK225 Platform",
    )

    dp = data_provider

    # FIX: bypass __getattr__ de Dash pour que app.data_provider fonctionne
    app.__dict__["data_provider"] = dp

    app.layout = build_layout(dp)

    # ── Callbacks ─────────────────────────────────────────────────
    import importlib
    for label, module in [
        ("clock_callbacks",     "dashboard.callbacks.clock_callbacks"),
        ("math_callbacks",      "dashboard.callbacks.math_callbacks"),
        ("company_callbacks",   "dashboard.callbacks.company_callbacks"),
        ("ai_callbacks",        "dashboard.callbacks.ai_callbacks"),
        ("backtest_callbacks",  "dashboard.callbacks.backtest_callbacks"),
    ]:
        try:
            mod = importlib.import_module(module)
            # Cherche register_*_callbacks ou register_*
            name = f"register_{label.replace('_callbacks','')}_callbacks"
            fn   = getattr(mod, name, None) or getattr(mod, f"register_{label}", None)
            if fn:
                _register(label, fn, app, dp)
        except ImportError as e:
            logger.warning(f"✗ {label} import: {e}")

    try:
        from dashboard.callbacks.execution_callbacks import register_execution_callbacks
        from execution.execution_engine import PaperTradingEngine
        register_execution_callbacks(app, dp, PaperTradingEngine())
        logger.info("✓ execution_callbacks")
    except Exception as e:
        logger.warning(f"✗ execution_callbacks: {e}")

    register_router(app, dp)
    return app