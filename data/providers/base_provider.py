from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pandas as pd


class BaseDataProvider(ABC):
    """
    Abstract base class for all data providers.

    All data sources (Yahoo, IBKR, etc.) must implement this interface.
    This ensures that the rest of the system is fully decoupled from
    specific data vendors.
    """

    @abstractmethod
    def get_prices(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Retrieve historical price data.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with MultiIndex (date, ticker) and OHLCV columns

        Raises:
            RuntimeError: If data retrieval fails
        """
        pass

    @abstractmethod
    def get_returns(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Compute returns from price data.

        Returns:
            DataFrame of returns
        """
        pass

    @abstractmethod
    def get_fundamentals(
        self,
        tickers: List[str]
    ) -> pd.DataFrame:
        """
        Retrieve fundamental data.

        Returns:
            DataFrame with fundamental metrics
        """
        pass

    @abstractmethod
    def get_market_cap(
        self,
        tickers: List[str]
    ) -> pd.Series:
        """
        Retrieve market capitalizations.

        Returns:
            Series indexed by ticker
        """
        pass

    @abstractmethod
    def get_volume(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Retrieve volume data.

        Returns:
            DataFrame of volumes
        """
        pass

    @abstractmethod
    def get_fx_rates(
        self,
        base: str,
        quote: str,
        start_date: str,
        end_date: str
    ) -> pd.Series:
        """
        Retrieve FX rates.

        Returns:
            Series of FX rates
        """
        pass