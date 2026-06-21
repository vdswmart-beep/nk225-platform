from typing import Optional
from .yahoo_provider import YahooDataProvider
from .ibkr_provider import IBKRDataProvider


class ProviderFactory:
    """
    Factory class to instantiate the correct data provider.
    """

    @staticmethod
    def get_provider(
        mode: str,
        ibkr_client: Optional[object] = None
    ):
        """
        Args:
            mode: "backtest" or "live"
            ibkr_client: Required if mode == "live"

        Returns:
            Instance of BaseDataProvider
        """
        if mode == "backtest":
            return YahooDataProvider()

        elif mode == "live":
            if ibkr_client is None:
                raise ValueError("IBKR client required for live mode")
            return IBKRDataProvider(ibkr_client)

        else:
            raise ValueError(f"Unknown mode: {mode}")