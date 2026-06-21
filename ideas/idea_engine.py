# ideas/idea_engine.py — FIXED (BUG-08: fillna(0) retiré — corrompt le scoring financier)

import pandas as pd
import numpy as np


class IdeaEngine:

    def __init__(self, config=None):
        self.config = config or {}

    def generate(self, feature_matrix, research_results, fundamentals):
        """
        Combine toutes les sources pour créer l'univers d'idées.

        Ne fait PAS de fillna global — les NaN sont gérés individuellement
        par IdeaScorer.normalize() qui retourne 0 si une série est entièrement NaN.
        """
        df = feature_matrix.copy()

        if research_results is not None:
            df = df.merge(research_results, on="ticker", how="left")

        if fundamentals is not None:
            # Garder uniquement les colonnes utiles du df fundamentals
            fund_cols = ["ticker"] + [
                c for c in fundamentals.columns
                if c not in df.columns or c == "ticker"
            ]
            df = df.merge(fundamentals[fund_cols], on="ticker", how="left")

        df = df.drop_duplicates(subset=["ticker"])

        # FIX BUG-08: NE PAS faire fillna(0) sur l'ensemble du DataFrame.
        # Remplir uniquement les colonnes catégorielles (non-numériques) si vide.
        str_cols = df.select_dtypes(include="object").columns.difference(["ticker"])
        df[str_cols] = df[str_cols].fillna("")

        # Les colonnes numériques restent NaN — IdeaScorer les gère proprement.
        return df