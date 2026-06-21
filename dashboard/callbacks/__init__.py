# dashboard/callbacks/__init__.py

from dashboard.callbacks.clock_callbacks   import register_clock_callbacks
from dashboard.callbacks.company_callbacks import register_company_callbacks
from dashboard.callbacks.math_callbacks    import register_math_callbacks
from dashboard.callbacks.ai_callbacks      import register_ai_callbacks


def register_callbacks(app):
    register_clock_callbacks(app)
    register_company_callbacks(app)
    register_math_callbacks(app)
    register_ai_callbacks(app)
