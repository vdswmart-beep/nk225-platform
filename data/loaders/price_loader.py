# data/loaders/price_loader.py — FIXED (BUG-07: MultiIndex yfinance robuste + normalisation colonnes)

from typing import List, Optional
import pandas as pd
import numpy as np

from data.providers.base_provider import BaseDataProvider


class PriceLoader:
    """
    Loader avancé pour les données de prix.

    Normalise la structure yfinance (MultiIndex variable selon version et nombre
    de tickers) en un format standard (date × ticker) avec colonnes en minuscule.
    """

    def __init__(self, provider: BaseDataProvider):
        self.provider = provider

    # ── Normalisation yfinance ──────────────────────────────────────────────
    @staticmethod
    def _normalize_yfinance(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
        """
        Normalise le DataFrame brut de yfinance en MultiIndex (date, ticker).

        yfinance >= 0.2.50 peut retourner :
          - MultiIndex colonnes (Price, Ticker) si plusieurs tickers
          - Index simple si un seul ticker
        On standardise vers un index (date, ticker) avec colonnes OHLCV minuscules.
        """
        if df is None or df.empty:
            return df

        # Cas multi-tickers : colonnes MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            # Niveaux possibles : (field, ticker) ou (ticker, field)
            lvl0 = df.columns.get_level_values(0).unique().tolist()
            lvl1 = df.columns.get_level_values(1).unique().tolist()

            # Déterminer lequel est le champ vs le ticker
            ohlcv = {"Open", "High", "Low", "Close", "Volume",
                     "open", "high", "low", "close", "volume"}
            if set(lvl0) & ohlcv:
                # niveau 0 = champ, niveau 1 = ticker → stack niveau 1
                df = df.stack(level=1)
            else:
                # niveau 0 = ticker, niveau 1 = champ → stack niveau 0
                df = df.stack(level=0)

            df.index.names = ["date", "ticker"]

        # Cas un seul ticker : colonnes simples
        elif len(tickers) == 1:
            df = df.copy()
            df.index.name = "date"
            df["ticker"] = tickers[0]
            df = df.reset_index().set_index(["date", "ticker"])

        # Normaliser toutes les colonnes en minuscule — FIX BUG-03
        df.columns = [c.lower() for c in df.columns]

        return df.sort_index()

    # ── API publique ────────────────────────────────────────────────────────

    def load_prices(
        self,
        tickers:  List[str],
        start:    str,
        end:      str,
        fields:   Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Charge et normalise les données de prix.

        Returns:
            DataFrame MultiIndex (date, ticker) avec colonnes en minuscule.
        """
        raw = self.provider.get_prices(tickers, start, end)

        if raw is None or (hasattr(raw, "empty") and raw.empty):
            raise ValueError("Les données de prix sont vides.")

        df = self._normalize_yfinance(raw, tickers)

        if fields is not None:
            fields_lower = [f.lower() for f in fields]
            missing = set(fields_lower) - set(df.columns)
            if missing:
                raise ValueError(f"Champs manquants après normalisation : {missing}")
            df = df[fields_lower]

        # Déduplication
        df = df[~df.index.duplicated(keep="first")]
        return df

    def load_returns(
        self,
        tickers: List[str],
        start:   str,
        end:     str,
        method:  str = "simple",
    ) -> pd.DataFrame:
        """
        Calcule les rendements simples ou log.

        Returns:
            DataFrame (date × ticker).
        """
        prices = self.load_prices(tickers, start, end, fields=["close"])
        close  = prices["close"].unstack("ticker")

        if method == "simple":
            returns = close.pct_change()
        elif method == "log":
            returns = np.log(close / close.shift(1))
        else:
            raise ValueError(f"Méthode invalide : '{method}'. Utiliser 'simple' ou 'log'.")

        return returns.dropna(how="all")

    def load_volume(self, tickers: List[str], start: str, end: str) -> pd.DataFrame:
        df = self.load_prices(tickers, start, end, fields=["volume"])
        return df["volume"].unstack("ticker")

    def load_adv(
        self,
        tickers: List[str],
        start:   str,
        end:     str,
        window:  int = 20,
    ) -> pd.DataFrame:
        """Average Daily Volume sur `window` jours."""
        volume = self.load_volume(tickers, start, end)
        return volume.rolling(window).mean()

    def validate_data(self, df: pd.DataFrame, max_nan_ratio: float = 0.05) -> None:
        nan_ratio = df.isna().mean().mean()
        if nan_ratio > max_nan_ratio:
            raise ValueError(
                f"Trop de NaN dans les données : {nan_ratio:.2%} > {max_nan_ratio:.2%}"
            )

    def align_prices(self, df: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        if method == "ffill":
            return df.ffill()
        elif method == "bfill":
            return df.bfill()
        elif method is None:
            return df
        raise ValueError(f"Méthode de remplissage invalide : '{method}'")