# reporting/track_record.py — P2-C: Gestionnaire de track record auto-persistant

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger("TrackRecord")


class TrackRecord:
    """
    Enregistre automatiquement chaque trade et met à jour le track record Excel.

    Usage :
        tr = TrackRecord()
        tr.log_trade(ticker="7203.T", action="BUY", qty=100, price=2950, weight=0.05)
        tr.save_excel()   # mis à jour automatiquement à chaque trade si auto_save=True
    """

    def __init__(
        self,
        fund_name:     str  = "NK225 L/S Fund",
        base_nav:      float = 100_000_000,
        outputs_dir:   str  = "outputs",
        auto_save:     bool = True,
        json_backup:   bool = True,
    ):
        self.fund_name    = fund_name
        self.nav          = base_nav
        self.outputs_dir  = Path(outputs_dir)
        self.auto_save    = auto_save
        self.json_backup  = json_backup
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        self._trades:   List[Dict] = []
        self._nav_log:  List[Dict] = []
        self._positions: Dict[str, Dict] = {}   # ticker → {qty, price, side, weight}

        # Charger l'état existant si disponible
        self._load_json()

    # ── Logging ──────────────────────────────────────────────────────────────

    def log_trade(
        self,
        ticker:    str,
        action:    str,       # "BUY" | "SELL"
        qty:       int,
        price:     float,
        weight:    float      = 0.0,
        side:      str        = "LONG",
        commission: float     = 0.0,
        slippage:  float      = 0.0,
        note:      str        = "",
    ) -> Dict:
        """Enregistre un trade et met à jour les positions."""
        trade = {
            "date":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ticker":     ticker,
            "action":     action,
            "side":       side,
            "qty":        qty,
            "price":      round(price, 2),
            "notional":   round(qty * price, 0),
            "weight":     round(weight, 4),
            "commission": round(commission, 2),
            "slippage":   round(slippage, 2),
            "total_cost": round(commission + slippage, 2),
            "nav":        round(self.nav, 0),
            "note":       note,
        }

        self._trades.append(trade)
        self._update_position(ticker, action, qty, price, weight, side)

        logger.info(
            f"Trade: {action} {qty} × {ticker} @ ¥{price:,.0f} "
            f"({side}) | notional ¥{qty*price:,.0f}"
        )

        if self.auto_save:
            self._save_json()
            self.save_excel()

        return trade

    def log_nav(self, nav: float, comment: str = "") -> None:
        """Enregistre la NAV quotidienne."""
        entry = {
            "date":    datetime.now().strftime("%Y-%m-%d"),
            "nav":     round(nav, 0),
            "comment": comment,
        }
        self._nav_log.append(entry)
        self.nav = nav
        logger.info(f"NAV: ¥{nav:,.0f}")

        if self.auto_save:
            self._save_json()

    # ── Positions ─────────────────────────────────────────────────────────────

    def _update_position(
        self, ticker: str, action: str, qty: int,
        price: float, weight: float, side: str,
    ) -> None:
        if ticker not in self._positions:
            self._positions[ticker] = {"qty": 0, "avg_price": 0.0, "side": side, "weight": 0.0}

        pos = self._positions[ticker]
        if action in ("BUY", "COVER"):
            new_qty   = pos["qty"] + qty
            pos["avg_price"] = (
                (pos["qty"] * pos["avg_price"] + qty * price) / new_qty
                if new_qty > 0 else price
            )
            pos["qty"] = new_qty
        elif action in ("SELL", "SHORT"):
            pos["qty"] -= qty
            if pos["qty"] == 0:
                pos["avg_price"] = 0.0
        pos["weight"] = weight
        pos["side"]   = side

    def get_positions(self) -> pd.DataFrame:
        """Retourne les positions courantes."""
        rows = [{"ticker": t, **v} for t, v in self._positions.items() if v["qty"] != 0]
        if not rows:
            return pd.DataFrame(columns=["ticker","qty","avg_price","side","weight"])
        return pd.DataFrame(rows)

    # ── Métriques sur le track record ────────────────────────────────────────

    def get_pnl_series(self) -> pd.Series:
        """Série de NAV journalière depuis les logs."""
        if not self._nav_log:
            return pd.Series(dtype=float)
        df = pd.DataFrame(self._nav_log)
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date")["nav"]

    def get_trade_df(self) -> pd.DataFrame:
        """DataFrame de tous les trades."""
        if not self._trades:
            return pd.DataFrame()
        return pd.DataFrame(self._trades)

    def summary(self) -> Dict:
        """Résumé rapide du track record."""
        trades_df = self.get_trade_df()
        nav_series = self.get_pnl_series()

        n_trades  = len(trades_df)
        buys      = (trades_df["action"] == "BUY").sum()  if n_trades > 0 else 0
        sells     = (trades_df["action"] == "SELL").sum() if n_trades > 0 else 0
        total_notional = trades_df["notional"].sum() if n_trades > 0 else 0

        return {
            "fund":             self.fund_name,
            "current_nav":      self.nav,
            "n_trades":         n_trades,
            "n_buys":           int(buys),
            "n_sells":          int(sells),
            "total_notional":   float(total_notional),
            "open_positions":   len([p for p in self._positions.values() if p["qty"] != 0]),
            "last_trade_date":  trades_df["date"].iloc[-1] if n_trades > 0 else "—",
        }

    # ── Persistance JSON ────────────────────────────────────────────────────

    def _json_path(self) -> Path:
        return self.outputs_dir / f"track_record_{self.fund_name.replace(' ','_')}.json"

    def _save_json(self) -> None:
        if not self.json_backup:
            return
        data = {
            "fund_name":  self.fund_name,
            "nav":        self.nav,
            "trades":     self._trades,
            "nav_log":    self._nav_log,
            "positions":  self._positions,
            "saved_at":   datetime.now().isoformat(),
        }
        with open(self._json_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_json(self) -> None:
        path = self._json_path()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._trades    = data.get("trades",    [])
            self._nav_log   = data.get("nav_log",   [])
            self._positions = data.get("positions", {})
            self.nav        = data.get("nav", self.nav)
            logger.info(
                f"Track record chargé : {len(self._trades)} trades "
                f"| NAV ¥{self.nav:,.0f}"
            )
        except Exception as e:
            logger.warning(f"Impossible de charger le track record JSON : {e}")

    # ── Export Excel ────────────────────────────────────────────────────────

    def save_excel(self, path: Optional[str] = None) -> Path:
        """
        Génère / met à jour le fichier Excel de track record.
        Appelle excel_exporter.export_live_trade() pour le log des trades.
        """
        from reporting.excel_exporter import export_live_trade

        if path is None:
            path = self.outputs_dir / f"live_track_{self.fund_name.replace(' ','_')}.xlsx"

        # Pour l'instant : ré-exporter le dernier trade ajouté
        if self._trades:
            last_trade = self._trades[-1]
            export_live_trade(last_trade, output_path=str(path))

        return Path(path)

    def save_full_excel(
        self,
        backtest_result=None,
        path: Optional[str] = None,
    ) -> Path:
        """
        Génère le rapport Excel complet depuis un BacktestResult.
        Peut être appelé après un backtest ou en fin de période.
        """
        from reporting.excel_exporter import export_track_record

        if path is None:
            date_str = datetime.now().strftime("%Y%m%d")
            path     = self.outputs_dir / f"track_record_full_{date_str}.xlsx"

        if backtest_result is not None:
            return export_track_record(
                backtest_result,
                output_path=str(path),
                fund_name=self.fund_name,
            )

        logger.warning("save_full_excel: pas de BacktestResult fourni.")
        return Path(path)
