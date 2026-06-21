from typing import List
import pandas as pd

from data.providers.base_provider import BaseDataProvider


class FundamentalsLoader:
    """
    Loader for fundamental data.
    """

    def __init__(self, provider: BaseDataProvider):
        self.provider = provider

    def load_fundamentals(self, tickers: List[str]) -> pd.DataFrame:
        return self.provider.get_fundamentals(tickers)

    def load_market_cap(self, tickers: List[str]) -> pd.Series:
        return self.provider.get_market_cap(tickers)