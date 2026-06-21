import pandas as pd
from data.providers.base_provider import BaseDataProvider


class MacroLoader:
    """
    Loader for macroeconomic and FX data.
    """

    def __init__(self, provider: BaseDataProvider):
        self.provider = provider

    def load_fx_rates(
        self,
        base: str,
        quote: str,
        start: str,
        end: str
    ) -> pd.Series:
        return self.provider.get_fx_rates(base, quote, start, end)