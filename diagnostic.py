#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 21:27:06 2026

@author: martinvanderstraten
"""

#!/usr/bin/env python
# diagnostic.py — À exécuter depuis la racine du projet : python diagnostic.py
#
# Teste chaque composant indépendamment et liste les erreurs précises.

import sys, traceback, importlib
sys.path.insert(0, ".")

OK   = "  ✓"
FAIL = "  ✗"
results = []

def test(label, fn):
    try:
        fn()
        results.append((True, label, None))
        print(f"{OK} {label}")
    except Exception as e:
        results.append((False, label, e))
        print(f"{FAIL} {label}")
        print(f"       → {type(e).__name__}: {e}")


print("\n" + "━"*60)
print("  NK225 PLATFORM — DIAGNOSTIC")
print("━"*60 + "\n")

# ── Config ────────────────────────────────────────────────────────
print("── CONFIG ──")
test("config.settings",  lambda: importlib.import_module("config.settings"))
test("config.universe",  lambda: importlib.import_module("config.universe"))
test("config.brokers",   lambda: importlib.import_module("config.brokers"))

# ── Data ──────────────────────────────────────────────────────────
print("\n── DATA ──")
test("data.data_service",           lambda: importlib.import_module("data.data_service"))
test("data.providers.yahoo_provider",lambda: importlib.import_module("data.providers.yahoo_provider"))
test("data.providers.ibkr_provider", lambda: importlib.import_module("data.providers.ibkr_provider"))
test("data.loaders.price_loader",    lambda: importlib.import_module("data.loaders.price_loader"))
test("data.loaders.fundamentals_loader",lambda: importlib.import_module("data.loaders.fundamentals_loader"))

# ── Features ──────────────────────────────────────────────────────
print("\n── FEATURES ──")
test("features.build_features",           lambda: importlib.import_module("features.build_features"))
test("features.momentum.momentum_features",lambda: importlib.import_module("features.momentum.momentum_features"))
test("features.volatility.volatility_features",lambda: importlib.import_module("features.volatility.volatility_features"))
test("features.technical.technical_features",  lambda: importlib.import_module("features.technical.technical_features"))
test("features.value.value_features",     lambda: importlib.import_module("features.value.value_features"))
test("features.quality.quality_features", lambda: importlib.import_module("features.quality.quality_features"))

# ── Portfolio ─────────────────────────────────────────────────────
print("\n── PORTFOLIO ──")
test("portfolio.portfolio_builder",lambda: importlib.import_module("portfolio.portfolio_builder"))
test("portfolio.optimizer",        lambda: importlib.import_module("portfolio.optimizer"))
test("portfolio.risk_parity",      lambda: importlib.import_module("portfolio.risk_parity"))
test("portfolio.hrp",              lambda: importlib.import_module("portfolio.hrp"))

# ── Ideas ─────────────────────────────────────────────────────────
print("\n── IDEAS ──")
test("ideas.idea_engine",       lambda: importlib.import_module("ideas.idea_engine"))
test("ideas.idea_scoring",      lambda: importlib.import_module("ideas.idea_scoring"))
test("ideas.idea_ranking",      lambda: importlib.import_module("ideas.idea_ranking"))
test("ideas.idea_explainer",    lambda: importlib.import_module("ideas.idea_explainer"))
test("ideas.ideas_orchestration",lambda: importlib.import_module("ideas.ideas_orchestration"))

# ── Research ──────────────────────────────────────────────────────
print("\n── RESEARCH ──")
test("research.ic_analysis",      lambda: importlib.import_module("research.ic_analysis"))
test("research.statistical_tests",lambda: importlib.import_module("research.statistical_tests"))

# ── Risk ──────────────────────────────────────────────────────────
print("\n── RISK ──")
test("risk.var",           lambda: importlib.import_module("risk.var"))
test("risk.drawdown",      lambda: importlib.import_module("risk.drawdown"))
test("risk.stress_testing",lambda: importlib.import_module("risk.stress_testing"))

# ── Pipelines ─────────────────────────────────────────────────────
print("\n── PIPELINES ──")
test("pipelines.master_pipeline",   lambda: importlib.import_module("pipelines.master_pipeline"))
test("pipelines.portfolio_pipeline",lambda: importlib.import_module("pipelines.portfolio_pipeline"))

# ── Backtest / Reporting ──────────────────────────────────────────
print("\n── BACKTEST / REPORTING ──")
test("backtesting.backtest_engine", lambda: importlib.import_module("backtesting.backtest_engine"))
test("reporting.excel_exporter",    lambda: importlib.import_module("reporting.excel_exporter"))
test("reporting.track_record",      lambda: importlib.import_module("reporting.track_record"))

# ── Dashboard ─────────────────────────────────────────────────────
print("\n── DASHBOARD ──")
test("dashboard.components.charts", lambda: importlib.import_module("dashboard.components.charts"))
test("dashboard.components.tables", lambda: importlib.import_module("dashboard.components.tables"))
test("dashboard.data_provider",     lambda: importlib.import_module("dashboard.data_provider"))
test("dashboard.layout",            lambda: importlib.import_module("dashboard.layout"))
test("dashboard.router",            lambda: importlib.import_module("dashboard.router"))

print("\n── DASHBOARD PAGES ──")
pages = ["overview","research_lab","idea_lab","math_lab","ai_lab",
         "portfolio_lab","risk_lab","backtest_lab","execution_lab","company_analyzer"]
for p in pages:
    test(f"dashboard.pages.{p}", lambda pg=p: importlib.import_module(f"dashboard.pages.{pg}"))

print("\n── DASHBOARD CALLBACKS ──")
cbs = ["clock_callbacks","math_callbacks","company_callbacks",
       "ai_callbacks","backtest_callbacks","execution_callbacks"]
for c in cbs:
    test(f"dashboard.callbacks.{c}", lambda cb=c: importlib.import_module(f"dashboard.callbacks.{cb}"))

# ── AI ────────────────────────────────────────────────────────────
print("\n── AI ──")
test("ai.grok_client",        lambda: importlib.import_module("ai.grok_client"))
test("ai.ollama_client",      lambda: importlib.import_module("ai.ollama_client"))
test("ai.ai_router",          lambda: importlib.import_module("ai.ai_router"))
test("ai.hypothesis_generator",lambda: importlib.import_module("ai.hypothesis_generator"))

# ── Execution ─────────────────────────────────────────────────────
print("\n── EXECUTION ──")
test("execution.execution_engine", lambda: importlib.import_module("execution.execution_engine"))

# ── Math Engine ───────────────────────────────────────────────────
print("\n── MATH ENGINE ──")
test("math_engine.statistical_models", lambda: importlib.import_module("math_engine.statistical_models"))
test("math_engine.hypothesis_testing", lambda: importlib.import_module("math_engine.hypothesis_testing"))

# ── Résumé ────────────────────────────────────────────────────────
passed = sum(1 for r in results if r[0])
failed = [r for r in results if not r[0]]

print("\n" + "━"*60)
print(f"  RÉSULTAT : {passed}/{len(results)} OK | {len(failed)} ERREUR(S)")
print("━"*60)

if failed:
    print("\n  ERREURS À CORRIGER :")
    for _, label, err in failed:
        print(f"\n  ✗ {label}")
        print(f"    {type(err).__name__}: {err}")