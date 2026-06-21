from typing import List, Optional
import pandas as pd

from data.providers.provider_factory import ProviderFactory
from data.loaders.price_loader import PriceLoader
from data.loaders.fundamentals_loader import FundamentalsLoader
from data.loaders.macro_loader import MacroLoader


class DataService:
    """
    Central data access layer.

    This is the ONLY entry point for all data access in the system.

    Responsibilities:
    - Instantiate correct provider (Yahoo or IBKR)
    - Expose clean API to strategies / backtests
    - Delegate to loaders
    """

    def __init__(
        self,
        mode: str = "backtest",
        ibkr_client: Optional[object] = None
    ):
        """
        Args:
            mode: "backtest" or "live"
            ibkr_client: Required for live mode
        """
        self.provider = ProviderFactory.get_provider(mode, ibkr_client)

        # Loaders
        self.price_loader = PriceLoader(self.provider)
        self.fundamentals_loader = FundamentalsLoader(self.provider)
        self.macro_loader = MacroLoader(self.provider)

    # =========================
    # PRICE DATA
    # =========================

    def get_prices(
        self,
        tickers: List[str],
        start: str,
        end: str
    ) -> pd.DataFrame:
        return self.price_loader.load_prices(tickers, start, end)

    def get_returns(
        self,
        tickers: List[str],
        start: str,
        end: str,
        method: str = "simple"
    ) -> pd.DataFrame:
        return self.price_loader.load_returns(tickers, start, end, method)

    def get_volume(
        self,
        tickers: List[str],
        start: str,
        end: str
    ) -> pd.DataFrame:
        return self.price_loader.load_volume(tickers, start, end)

    def get_adv(
        self,
        tickers: List[str],
        start: str,
        end: str,
        window: int = 20
    ) -> pd.DataFrame:
        return self.price_loader.load_adv(tickers, start, end, window)

    # =========================
    # FUNDAMENTALS
    # =========================

    def get_fundamentals(
        self,
        tickers: List[str]
    ) -> pd.DataFrame:
        return self.fundamentals_loader.load_fundamentals(tickers)

    def get_market_cap(
        self,
        tickers: List[str]
    ) -> pd.Series:
        return self.fundamentals_loader.load_market_cap(tickers)

    # =========================
    # MACRO / FX
    # =========================

    def get_fx_rates(
        self,
        base: str,
        quote: str,
        start: str,
        end: str
    ) -> pd.Series:
        return self.macro_loader.load_fx_rates(base, quote, start, end)