# Helios Capital — Long/Short Equity Research & Derivatives Platform

> A quantitative research, trading, and options-pricing platform built to institutional standards. Generates, analyses, and executes long/short equity strategies on the **EURO STOXX 50**, with a full European-options analytics desk and live IBKR paper-trading integration.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.18-cyan?logo=plotly)](https://dash.plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Why This Project

I built this platform out of a genuine interest in long/short equity investing and quantitative finance. L/S strategies are compelling because they separate alpha from market direction: the goal is not to call the market, but to identify **relative mispricings** between securities and express a view with controlled risk.

The EURO STOXX 50 is a strong universe for this: high dispersion across sectors (luxury, semiconductors, banks, energy, healthcare), a single currency (EUR) that removes FX noise, and deep, well-covered fundamental data. The index spans eight euro-zone countries and the continent's largest companies — LVMH, ASML, SAP, TotalEnergies, Siemens, Sanofi and more.

This tool is my attempt to build the research infrastructure a fundamental L/S analyst would actually use end to end — from factor scoring to walk-forward backtesting, paper-trade execution, and an options desk for hedging and expressing convex views.

---

## What It Does

A rigorous, data-driven workflow to:

1. **Score** every stock in the EURO STOXX 50 across multiple factor dimensions
2. **Rank** them into long and short candidates with conviction levels and an estimated holding horizon
3. **Validate** each idea with a full fundamental + momentum fiche before committing
4. **Backtest** the resulting L/S strategy with realistic transaction costs
5. **Execute** paper trades (Interactive Brokers, or a local Python simulator) with an automatic −6% stop-loss per position
6. **Price options** on the index constituents with a full Black-Scholes desk (Greeks, strategies, parity, vol surface), using real market implied volatility from IBKR when available

---

## Dashboard Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Overview | Live portfolio: positions, P&L per position, sector exposure, NAV |
| `/research` | Research Lab | Information-coefficient analysis, rolling Spearman, factor scores |
| `/ideas` | Idea Lab | Long/short candidates ranked by conviction — click any card for a full fiche (price, fundamentals, momentum, vol, beta, cross-sectional Z-scores) + one-click execution |
| `/math` | Math Lab | **Pair trading**: spread, z-score signals, cointegration, rolling beta/correlation, spread backtest |
| `/ai` | AI Lab | AI-generated investment hypotheses (Groq / Llama 3.3) |
| `/backtest` | Backtest Lab | Walk-forward backtesting with full performance metrics |
| `/portfolio` | Portfolio | NAV, allocation, positions table |
| `/risk` | Risk Lab | VaR, CVaR, drawdown profile, European stress tests (2008, COVID, ECB +50bps, EURO STOXX −20%) |
| `/watchlist` | Watchlist | Buy-side deep dive with price, technicals, valuation, financials, bull/bear, trade buttons |
| `/options` | **Options Lab** | European options desk: Pricer · Greeks · Strategies · Parity · Vol Surface |
| `/execution` | Execution Lab | Paper trading, order blotter, delta vs target weights |
| `/company` | Company Analyzer | Price history + fundamentals vs sector peers for any constituent |

---

## Options Lab — European Options Desk

A complete equity-derivatives analytics suite, priced on the EURO STOXX 50 constituents. The pricing engine is fully vectorised and framework-agnostic.

- **Pricer** — Black-Scholes price + full Greeks (desk units: vega/ρ per 1%, θ per day) for any strike/expiry/type, with a live payoff diagram.
- **Greeks Explorer** — interactive sliders (spot, strike, vol, maturity) that reprice Greeks instantly, with a delta-vs-spot profile for call and put.
- **Strategy Builder** — 11 strategies (spreads, butterflies, straddles, strangles, iron butterfly, covered call, protective put, fiduciary call…), each with net cost, max profit/loss, break-evens, aggregated book Greeks, and a P&L payoff chart.
- **Put-Call Parity** — residual check against the cash-and-carry relation `C − P = S·e⁻qT − K·e⁻rT`.
- **Volatility Surface** — 3-D IV surface (strike × maturity × IV), vol smiles by expiry, and the ATM term structure.

**Two data sources**: by default the desk uses a self-consistent theoretical chain built from the live Yahoo spot and a sector-calibrated skew (every premium is a Black-Scholes model value — an honest theoretical pricer). When TWS is running and the user opts in, the desk pulls **real market implied volatility from Interactive Brokers** (`reqMktData` tick 106 + model Greeks). A badge in the UI always shows which source is active.

---

## Key Features (Equity)

- **Sector-aware L/S scoring** — composite of momentum (40%), quality (25%), value (20%) and intra-sector positioning (15%), with Z-scores computed cross-sectionally and within each sector.
- **Idea Lab with manual validation** — the scoring engine generates ranked long/short candidates with a holding horizon by conviction; clicking a card opens a full fiche so every trade is checked before execution.
- **Pair trading** — spread = log(A) − β·log(B) with rolling OLS beta, z-score entry/exit signals, Engle-Granger cointegration and ADF tests, rolling correlation, and a spread backtest.
- **Automatic −6% stop-loss** — a monitor checks open positions every 60 seconds and closes any breaching −6% P&L (IBKR or simulated).
- **Walk-forward backtesting** — train/test windows that avoid look-ahead bias, realistic slippage and commission, full metrics (Sharpe, Sortino, Calmar, Max Drawdown, VaR/CVaR), monthly PnL heatmap, and one-click Excel export.
- **Live IBKR paper trading** — launch with `--mode live` to connect TWS: the dashboard reads the real account NAV and routes orders to Euronext / Xetra / Borsa Italiana / BME via SMART routing.

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Dashboard | Dash 2.18 · Plotly · Dash Bootstrap Components |
| Data | Yahoo Finance (yfinance 1.x) · IBKR TWS API (ib-insync, execution + real IV) |
| Computation | pandas · NumPy · SciPy · statsmodels |
| Options engine | Vectorised Black-Scholes-Merton · Newton-Raphson + Brent IV solver · scattered-data vol surface (griddata) |
| AI | Groq API (Llama 3.3-70B) |
| Reporting | openpyxl (Excel track record) |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/vdswmart-beep/nk225-platform.git
cd nk225-platform
pip install -r requirements.txt

# 2. Configure (optional — for AI Lab)
cp .env.example .env
# Add a free Groq key (console.groq.com): GROQ_API_KEY=gsk_...

# 3. Launch
python run_dashboard.py                      # Full EURO STOXX 50 (50 tickers)
python run_dashboard.py --universe liquid40   # 40 most liquid (faster start)
python run_dashboard.py --mode live           # Connect IBKR paper trading (port 7497)
```

**IBKR paper trading** (optional): open TWS, enable *Edit → Global Configuration → API → Enable ActiveX and Socket Clients*, port 7497, then run with `--mode live`. Yahoo Finance is always used for research data; IBKR is used for order routing and (optionally) real option implied volatility. Without `--mode live`, paper trading is simulated locally in Python.

---

## Architecture

```
.
├── config/        # EURO STOXX 50 universe (50 tickers), settings, factor weights
├── data/          # Provider pattern: Yahoo Finance, loaders, cache
├── features/      # Momentum, volatility, value, quality, technical factors
├── ideas/         # Sector-aware L/S scoring engine
├── research/      # IC analysis, statistical tests
├── portfolio/     # Risk Parity, HRP, Mean-Variance optimiser
├── risk/          # VaR, CVaR, drawdown, stress testing
├── backtesting/   # Walk-forward engine, performance metrics
├── execution/     # Paper trading simulation + IBKR live connector (thread-safe)
├── reporting/     # Excel track-record exporter
├── ai/            # Groq / Grok / Ollama clients with auto-routing
├── options/       # European-options desk (framework-agnostic engine)
│   ├── pricing/     # Black-Scholes, implied vol solver, put-call parity
│   ├── volatility/  # Smiles, term structure, 3-D surface
│   ├── strategies/  # 11 strategies + registry, payoff/Greek analytics
│   ├── option_chain.py   # Tidy DataFrame wrapper
│   ├── mock_provider.py  # Synthetic chain from live Yahoo spot
│   └── ibkr_provider.py  # Real market IV from TWS
├── pipelines/     # Master pipeline: Data → Features → Ideas → Portfolio → Risk
└── dashboard/     # 12-page Dash application (dark theme)
```

---

## Roadmap

- [ ] Cointegration-based pairs scanner across the full index
- [ ] Factor regime detection (risk-on / risk-off)
- [ ] Multi-strategy portfolio with correlation-aware sizing
- [ ] Options strategy backtester (roll a delta-hedged position through history)

---

## Disclaimer

Built for educational and research purposes. The signals and option prices generated do not constitute investment advice. Always validate strategies in paper trading before deploying real capital. Trading involves risk of loss.

---

*Built with Python 3.12 — EURO STOXX 50 Long/Short Equity Research & Derivatives Platform*