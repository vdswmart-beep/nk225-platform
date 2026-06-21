# pipelines/data_pipeline.py

import logging
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional
from data.data_service import DataService

logger = logging.getLogger("DataPipeline")


@dataclass
class DataOutputs:
    prices:       pd.DataFrame = field(default_factory=pd.DataFrame)
    fundamentals: pd.DataFrame = field(default_factory=pd.DataFrame)
    returns:      pd.DataFrame = field(default_factory=pd.DataFrame)


class DataPipeline:

    def __init__(self, data_service: DataService):
        self.ds = data_service

    def run(self, tickers: List[str], start: str, end: str) -> DataOutputs:
        logger.info(f"Loading data for {len(tickers)} tickers: {start} → {end}")

        prices = self.ds.get_prices(tickers, start, end)
        logger.info(f"Prices shape: {prices.shape}")

        fundamentals = self.ds.get_fundamentals(tickers)
        logger.info(f"Fundamentals shape: {fundamentals.shape}")

        returns = self.ds.get_returns(tickers, start, end)
        logger.info(f"Returns shape: {returns.shape}")

        return DataOutputs(prices=prices, fundamentals=fundamentals, returns=returns)
