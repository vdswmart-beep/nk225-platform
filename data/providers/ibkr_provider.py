# data/providers/ibkr_provider.py — P3-A: IBKR provider implémenté (remplace NotImplementedError)

from __future__ import annotations
import logging
from typing import List
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from .base_provider import BaseDataProvider

logger = logging.getLogger("IBKRProvider")


class IBKRDataProvider(BaseDataProvider):
    """
    Interactive Brokers data provider (mode live).

    Utilise ib_insync pour se connecter à TWS/Gateway.
    Fallback automatique sur Yahoo Finance si IBKR est indisponible.
    """

    EXCHANGE  = "TSEJ"
    CURRENCY  = "JPY"
    TIMEOUT   = 10       # secondes

    def __init__(self, client=None, host: str = "127.0.0.1",
                 port: int = 7497, client_id: int = 1):
        self._client    = client
        self._host      = host
        self._port      = port
        self._client_id = client_id
        self._ib        = None
        self._connected = False
        self._yahoo_fallback = None   # initialisé à la demande

        if client is not None:
            self._ib = client
            self._connected = True
            logger.info("IBKRProvider: client externe fourni")
        else:
            self._connect()

    # ── Connexion ─────────────────────────────────────────────────

    def _connect(self) -> bool:
        try:
            from ib_insync import IB
            self._ib = IB()
            self._ib.connect(self._host, self._port, clientId=self._client_id,
                             timeout=self.TIMEOUT)
            self._connected = self._ib.isConnected()
            if self._connected:
                logger.info(f"IBKR connecté → {self._host}:{self._port}")
            else:
                logger.warning("IBKR non connecté — fallback Yahoo activé")
        except Exception as e:
            logger.warning(f"IBKR connexion échouée : {e} — fallback Yahoo activé")
            self._connected = False
        return self._connected

    def _get_fallback(self):
        if self._yahoo_fallback is None:
            from .yahoo_provider import YahooDataProvider
            self._yahoo_fallback = YahooDataProvider()
            logger.info("Yahoo fallback initialisé")
        return self._yahoo_fallback

    def is_connected(self) -> bool:
        if self._ib is None:
            return False
        try:
            return self._ib.isConnected()
        except Exception:
            return False

    def reconnect(self) -> bool:
        """Tente une reconnexion automatique."""
        logger.info("Tentative de reconnexion IBKR...")
        return self._connect()

    # ── Contrats ──────────────────────────────────────────────────

    def _make_contract(self, ticker: str):
        """Crée un contrat IBKR depuis un ticker Yahoo (.T suffix)."""
        from ib_insync import Stock
        code = ticker.replace(".T", "")
        return Stock(code, self.EXCHANGE, self.CURRENCY)

    # ── Prix historiques ──────────────────────────────────────────

    def get_prices(self, tickers: List[str], start_date: str,
                   end_date: str) -> pd.DataFrame:
        if not self.is_connected():
            logger.warning("get_prices: IBKR offline → Yahoo fallback")
            return self._get_fallback().get_prices(tickers, start_date, end_date)

        try:
            from ib_insync import util
            all_dfs = {}
            end_dt  = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            duration_days = (end_dt - start_dt).days
            duration_str  = f"{duration_days} D"

            for ticker in tickers:
                contract = self._make_contract(ticker)
                self._ib.qualifyContracts(contract)
                bars = self._ib.reqHistoricalData(
                    contract,
                    endDateTime   = end_dt.strftime("%Y%m%d %H:%M:%S"),
                    durationStr   = duration_str,
                    barSizeSetting= "1 day",
                    whatToShow    = "TRADES",
                    useRTH        = True,
                    formatDate    = 1,
                )
                if bars:
                    df = util.df(bars)[["date","open","high","low","close","volume"]]
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.set_index("date")
                    df["ticker"] = ticker
                    all_dfs[ticker] = df

            if not all_dfs:
                raise ValueError("Aucun prix IBKR récupéré")

            combined = pd.concat(all_dfs.values())
            combined = combined.reset_index().set_index(["date","ticker"])
            logger.info(f"IBKR prix: {len(all_dfs)} tickers chargés")
            return combined

        except Exception as e:
            logger.error(f"get_prices IBKR échoué : {e} → Yahoo fallback")
            return self._get_fallback().get_prices(tickers, start_date, end_date)

    def get_returns(self, tickers: List[str], start_date: str,
                    end_date: str) -> pd.DataFrame:
        prices = self.get_prices(tickers, start_date, end_date)
        if isinstance(prices.index, pd.MultiIndex):
            close = prices["close"].unstack("ticker")
        else:
            close = prices["close"] if "close" in prices.columns else prices["Close"]
        return close.pct_change().dropna(how="all")

    # ── Prix temps réel ───────────────────────────────────────────

    def get_live_price(self, ticker: str) -> dict:
        """Prix en temps réel pour un ticker."""
        if not self.is_connected():
            logger.warning(f"get_live_price: IBKR offline pour {ticker}")
            return {"ticker": ticker, "price": None, "bid": None, "ask": None}

        try:
            from ib_insync import MarketOrder
            contract = self._make_contract(ticker)
            self._ib.qualifyContracts(contract)
            ticker_data = self._ib.reqMktData(contract, "", False, False)
            self._ib.sleep(1)
            return {
                "ticker": ticker,
                "price":  ticker_data.last,
                "bid":    ticker_data.bid,
                "ask":    ticker_data.ask,
                "volume": ticker_data.volume,
                "time":   datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"get_live_price {ticker}: {e}")
            return {"ticker": ticker, "price": None, "error": str(e)}

    def get_live_prices(self, tickers: List[str]) -> pd.DataFrame:
        """Prix en temps réel pour une liste de tickers."""
        rows = [self.get_live_price(t) for t in tickers]
        return pd.DataFrame(rows)

    # ── Fondamentaux ──────────────────────────────────────────────

    def get_fundamentals(self, tickers: List[str]) -> pd.DataFrame:
        """Toujours via Yahoo (IBKR fundamentals = add-on payant)."""
        logger.info("Fondamentaux via Yahoo Finance (IBKR fundamentals = add-on)")
        return self._get_fallback().get_fundamentals(tickers)

    def get_market_cap(self, tickers: List[str]) -> pd.Series:
        fund = self.get_fundamentals(tickers)
        return fund["marketCap"] if "marketCap" in fund.columns else pd.Series(dtype=float)

    def get_volume(self, tickers: List[str], start_date: str,
                   end_date: str) -> pd.DataFrame:
        prices = self.get_prices(tickers, start_date, end_date)
        if isinstance(prices.index, pd.MultiIndex):
            return prices["volume"].unstack("ticker")
        return prices[["volume"]] if "volume" in prices.columns else pd.DataFrame()

    def get_fx_rates(self, base: str, quote: str, start_date: str,
                     end_date: str) -> pd.Series:
        return self._get_fallback().get_fx_rates(base, quote, start_date, end_date)

    # ── Positions courantes ───────────────────────────────────────

    def get_positions(self) -> pd.DataFrame:
        """Positions actuelles du compte IBKR."""
        if not self.is_connected():
            return pd.DataFrame()
        try:
            positions = self._ib.positions()
            rows = []
            for pos in positions:
                rows.append({
                    "account":  pos.account,
                    "ticker":   pos.contract.symbol + ".T",
                    "qty":      pos.position,
                    "avg_cost": pos.avgCost,
                    "market_value": pos.position * pos.avgCost,
                })
            return pd.DataFrame(rows)
        except Exception as e:
            logger.error(f"get_positions: {e}")
            return pd.DataFrame()

    def get_account_summary(self) -> dict:
        """Résumé du compte (NAV, cash, etc.)."""
        if not self.is_connected():
            return {}
        try:
            summary = self._ib.accountSummary()
            return {item.tag: item.value for item in summary}
        except Exception as e:
            logger.error(f"get_account_summary: {e}")
            return {}