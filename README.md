# NK225 — Equity Research & Trading Platform

> Plateforme long/short d'equity research sur le Nikkei 225, construite avec des standards hedge fund.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.18-cyan?logo=plotly)](https://dash.plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 Aperçu

Plateforme quantitative complète pour l'analyse et le trading d'actions japonaises (Nikkei 225) en stratégie **long/short market-neutral**. Conçue avec les standards d'un outil interne de hedge fund.

**[🔗 Demo live →](https://nk225-platform.onrender.com)**

![Dashboard Screenshot](docs/screenshot.png)

---

## ✨ Fonctionnalités

### 📊 Research & Analyse
- **Factor scoring** multi-facteurs (qualité, momentum, valeur, croissance, risque) avec ajustement de régime de marché
- **IC Analysis** (Information Coefficient) sur 7 facteurs validés statistiquement
- **Math Lab** : OLS, PCA, ADF, coïntégration, rolling beta, corrélation
- **AI Lab** : Hypothèses d'investissement générées par Grok-3 ou Ollama (local)

### 📈 Backtesting
- Walk-forward backtesting avec fenêtres train/test configurables
- 15 métriques : Sharpe, Sortino, Calmar, MaxDD, Win Rate, Profit Factor, VaR 95%, CVaR 95%
- Coûts de transaction réalistes (slippage + commission)
- Export track record Excel (5 feuilles : Summary, Equity Curve, Drawdown, Monthly PnL, Trade Log)

### ⚡ Execution
- **Paper trading** avec simulation réaliste (slippage log-normal, spread bid/ask, latence)
- **Live trading IBKR** via TWS (port 7497 paper / 7496 live)
- Bouton "Valider Ordre" avec prévisualisation + blotter en temps réel
- Track record auto-persistant (JSON + Excel)

### 🗂 Données
- Univers Nikkei 225 (185 composants mappés Yahoo Finance)
- Cache intelligent 24h (évite les re-téléchargements)
- Provider pattern : Yahoo Finance (backtest) / IBKR (live) avec fallback automatique

---

## 🏗 Architecture

```
Data → Features → Research → Ideas → Portfolio → Risk → Execution
         ↓            ↓         ↓          ↓         ↓
    factor_matrix  ic_stats  longs/   weights/   orders/
    (21 features)           shorts   risk_metrics  fills
                               ↓
                        Dashboard (Dash)
                               ↓
                     AI Lab (Grok / Ollama)
                               ↓
                    Backtest + Track Record Excel
```

**Stack technique**
- Python 3.12 · Dash 2.18 · Plotly · pandas · numpy · scipy · scikit-learn
- yfinance · ib-insync · statsmodels · openpyxl
- xAI Grok-3 (cloud) ou Ollama (local)

---

## 🚀 Installation

```bash
# 1. Cloner le repo
git clone https://github.com/<username>/nk225-platform.git
cd nk225-platform

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env : ajouter GROK_API_KEY si souhaité

# 5. Lancer le dashboard
python run_dashboard.py --universe default   # 10 tickers, démarrage rapide
```

---

## 📖 Usage

```bash
# Dashboard — univers complet Nikkei 225
python run_dashboard.py --universe full

# Dashboard avec backtest pré-chargé au démarrage
python run_dashboard.py --universe liquid40 --run-backtest

# Pipeline headless backtest + export Excel
python run.py --mode walkforward --universe liquid40 --export-excel

# Mode live IBKR (TWS requis sur port 7497)
python run_dashboard.py --mode live
```

### Pages disponibles

| URL | Description |
|-----|-------------|
| `/` | Overview — NAV, positions, univers |
| `/research` | IC Analysis, factor scores |
| `/ideas` | Idées long/short rankées |
| `/math` | OLS, PCA, ADF, rolling beta |
| `/ai` | Hypothèses IA (Grok / Ollama) |
| `/backtest` | Walk-forward + export Excel |
| `/portfolio` | NAV, allocation, performance |
| `/risk` | VaR, CVaR, drawdown, stress tests |
| `/execution` | Ordres, blotter, paper/live |
| `/company` | Deep-dive single stock |

---

## 🔧 Configuration

Toutes les options dans `.env` :

```env
DATA_MODE=backtest          # backtest | live
GROK_API_KEY=xai-...        # Optionnel — Grok-3
USE_OLLAMA=false            # true = IA locale (Ollama)
PORTFOLIO_METHOD=risk_parity
```

---

## ☁️ Déploiement (Render.com)

```bash
# 1. Push sur GitHub
git add . && git commit -m "Initial deploy" && git push

# 2. render.com → New → Blueprint → connecter le repo
# Render lit render.yaml et déploie automatiquement

# 3. Ajouter GROK_API_KEY dans Environment Variables sur Render
```

---

## 📁 Structure

```
nk225-platform/
├── config/          # Univers 225 tickers, settings, facteurs
├── data/            # Providers (Yahoo/IBKR), loaders, cache
├── features/        # Momentum, volatility, value, quality, technical
├── ideas/           # Scoring, ranking, explainer
├── research/        # IC analysis, tests statistiques
├── portfolio/       # Risk parity, HRP, MV optimizer
├── risk/            # VaR, CVaR, drawdown, stress tests
├── backtesting/     # Walk-forward engine, métriques
├── execution/       # Paper trading, IBKR live
├── reporting/       # Excel track record, trade log
├── ai/              # Grok client, Ollama client, AI router
├── pipelines/       # Master pipeline (Data→Execution)
├── dashboard/       # App Dash (10 pages, callbacks, components)
├── run.py           # Pipeline headless
└── run_dashboard.py # Dashboard web
```

---

## 📊 Métriques calculées

| Catégorie | Métriques |
|-----------|-----------|
| Performance | Total Return, Ann. Return, Ann. Volatility |
| Risk-adjusted | Sharpe, Sortino, Calmar |
| Drawdown | Max Drawdown, Duration maximale |
| Tail Risk | VaR 95%, CVaR 95%, Skewness, Kurtosis |
| Execution | Win Rate, Profit Factor |
| Portfolio | Gross/Net Exposure, Beta, Turnover |

---

## ⚠️ Disclaimer

Ce projet est à vocation éducative et de recherche. Les signaux générés ne constituent pas des conseils d'investissement. Le trading live implique des risques de perte en capital. Toujours valider en paper trading avant de passer en mode live.

---

*Développé avec Python 3.12 — Nikkei 225 Long/Short Equity Research Platform*