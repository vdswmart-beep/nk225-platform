# NK225 — Long/Short Equity Research Platform

> A professional-grade quantitative research and trading platform for the Nikkei 225, built with hedge fund standards. Designed to generate, analyse, and execute long/short equity strategies on Japanese equities.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.18-cyan?logo=plotly)](https://dash.plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Why This Project

I built this platform out of a genuine passion for long/short equity investing and quantitative finance. Long/short strategies fascinate me because they separate alpha generation from market direction — the goal is not to predict whether the market goes up or down, but to identify **relative mispricings** between securities.

The Nikkei 225 is a particularly interesting universe for L/S strategies:
- **High dispersion** across sectors (automotive, semiconductors, financials, healthcare) creates abundant pair opportunities
- **Macro sensitivity** to USD/JPY and Bank of Japan policy generates recurring factor rotations
- **Structural inefficiencies** persist due to cross-shareholding structures and late adoption of shareholder returns

This tool is my attempt to build the research infrastructure a fundamental L/S analyst would need — from factor scoring to walk-forward backtesting to paper trade execution.

---

## What It Does

### The Core Problem It Solves
Most retail investors either go long-only or have no systematic framework to evaluate short candidates. This platform provides a rigorous, data-driven workflow to:
1. **Score** every stock in the Nikkei 225 across 5 factor dimensions
2. **Rank** them into long and short candidates with conviction levels
3. **Backtest** the resulting L/S strategy with realistic transaction costs
4. **Execute** paper trades and track the portfolio's live performance
5. **Analyse** each position with AI-generated investment theses

---

## Platform Overview

```
Data (Yahoo Finance / IBKR)
  ↓
Feature Engineering (Momentum · Value · Quality · Volatility · Technical)
  ↓
Factor Scoring & IC Analysis
  ↓
Idea Generation (LONG / SHORT ranked by conviction)
  ↓
Portfolio Construction (Risk Parity · HRP · Mean-Variance)
  ↓
Walk-Forward Backtesting (out-of-sample validation)
  ↓
Risk Management (VaR · CVaR · Drawdown · Stress Tests)
  ↓
Paper Trade Execution (slippage · commission simulation)
  ↓
Track Record (Excel export · PnL attribution)
```

---

## Key Features

### Research Lab
- **IC Analysis** — Spearman rank correlation between factor signals and forward returns, computed on a rolling basis to detect regime changes
- **Factor Scores** — 7 quantitative factors per stock: momentum (1M/3M/6M/12M), realised volatility, RSI, and fundamental ratios
- Identifies which factors are currently predictive and which have decayed

### Idea Lab
- Scores each Nikkei 225 constituent on a 0–100 composite scale
- Classifies stocks as **LONG** (score > 55) or **SHORT** (score < 45) with HIGH / MEDIUM / LOW conviction
- Displays thesis, key catalysts, and risk factors for each idea

### Backtest Lab
- **Walk-forward backtesting** with configurable train/test windows (avoids look-ahead bias)
- Realistic simulation: slippage (5 bps), commission (3 bps), bid/ask spread
- Full performance metrics: Sharpe, Sortino, Calmar, Max Drawdown, Win Rate, Profit Factor, VaR 95%, CVaR 95%
- Monthly PnL heatmap and rolling Sharpe for regime analysis
- One-click **Excel export** of the complete track record

### Math Lab
- OLS factor regression with t-stats and p-values
- PCA decomposition of return covariance
- Rolling beta (63-day window) between any two stocks
- Return correlation heatmap across the full universe
- Statistical tests: ADF stationarity, Jarque-Bera normality, cointegration (for pair trades)

### AI Lab (Groq / Llama 3.3)
- Generates structured investment hypotheses grounded in live fundamental data
- Supports: single-stock analysis, long/short pair trade thesis, portfolio commentary
- Powered by Groq's Llama 3.3-70B (fast inference, free tier available)

### Risk Lab
- VaR 95% and CVaR 95% (historical simulation)
- Drawdown profile and maximum drawdown duration
- Stress tests: 2008 crisis, COVID crash, JPY +10% appreciation, BoJ rate hike +50bps

### Execution Lab
- Paper trading engine with realistic fill simulation (log-normal slippage, bid/ask spread, latency)
- Order form: BUY / SELL / COVER with MARKET or LIMIT order types
- Live order blotter and delta display vs target weights
- Auto-logs every trade to a persistent track record (JSON + Excel)
- Architecture ready for IBKR live trading (TWS API)

### Company Analyzer
- Price history chart with volume
- Full fundamental panel with **sector peer comparison**: P/E, P/B, EV/EBITDA, ROE, ROA — each benchmarked vs sector average with ▲/▼ indicators

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Dashboard | Dash 2.18 · Plotly · Dash Bootstrap Components |
| Data | Yahoo Finance (yfinance) · IBKR TWS API (ib-insync) |
| Computation | pandas · NumPy · SciPy · scikit-learn · statsmodels |
| Portfolio | Custom Risk Parity · HRP · Mean-Variance Optimiser |
| AI | Groq API (Llama 3.3-70B) · xAI Grok-3 · Ollama (local fallback) |
| Reporting | openpyxl (Excel) · JSON track record |

---

## Dashboard Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Overview | NAV equity curve, L/S idea summary, universe |
| `/research` | Research Lab | IC analysis, rolling Spearman, factor scores |
| `/ideas` | Idea Lab | Long/short candidates ranked by conviction |
| `/math` | Math Lab | OLS, PCA, ADF, cointegration, rolling beta |
| `/ai` | AI Lab | AI-generated investment hypotheses |
| `/backtest` | Backtest Lab | Walk-forward backtesting with full metrics |
| `/portfolio` | Portfolio | NAV, allocation, positions table |
| `/risk` | Risk Lab | VaR, CVaR, stress tests, drawdown profile |
| `/execution` | Execution Lab | Paper trading, order blotter, delta tracking |
| `/company` | Company Analyzer | Price history + fundamentals vs sector peers |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/vdswmart-beep/nk225-platform.git
cd nk225-platform
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your Groq API key (free at console.groq.com):
# GROQ_API_KEY=gsk_...

# 3. Launch
python run_dashboard.py                      # Full Nikkei 225 (185 tickers)
python run_dashboard.py --universe liquid40  # 40 most liquid tickers (fast start)
```

---

## Architecture

```
nk225-platform/
├── config/       # Universe (185 tickers), settings, factor weights
├── data/         # Provider pattern: Yahoo Finance / IBKR, loaders, cache
├── features/     # Momentum, volatility, value, quality, technical factors
├── ideas/        # Scoring engine, ranking, explainer
├── research/     # IC analysis, statistical tests
├── portfolio/    # Risk Parity, HRP, Mean-Variance optimiser
├── risk/         # VaR, CVaR, drawdown, stress testing
├── backtesting/  # Walk-forward engine, performance metrics
├── execution/    # Paper trading simulation, IBKR live connector
├── reporting/    # Excel track record exporter, trade logger
├── ai/           # Groq, Grok, Ollama clients with auto-routing
├── pipelines/    # Master pipeline: Data → Ideas → Portfolio → Risk
└── dashboard/    # 10-page Dash application
```

---

## Roadmap

- [ ] Custom pair trade backtesting (e.g. Long Toyota / Short Honda)
- [ ] Cointegration-based pairs scanner across full Nikkei 225
- [ ] IBKR live execution (production-ready architecture already in place)
- [ ] Factor regime detection (risk-on / risk-off auto-switching)
- [ ] Multi-strategy portfolio with correlation-aware position sizing

---

## Disclaimer

This project is built for educational and research purposes. The signals generated do not constitute investment advice. Always validate strategies in paper trading before deploying real capital.

---

*Built with Python 3.12 — Nikkei 225 Long/Short Equity Research Platform*