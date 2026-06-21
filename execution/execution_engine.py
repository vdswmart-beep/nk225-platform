# execution/execution_engine.py — P3-C: Moteur d'exécution complet
#
# Modes :
#   paper — simulation réaliste (slippage, frais, délai)
#   live  — ordres réels via IBKR TWS

from __future__ import annotations

import logging
import time
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger("ExecutionEngine")


# ══════════════════════════════════════════════════════
#  STRUCTURES
# ══════════════════════════════════════════════════════

@dataclass
class Order:
    ticker:     str
    action:     str          # "BUY" | "SELL"
    qty:        int
    order_type: str          # "MARKET" | "LIMIT"
    limit_price: Optional[float] = None
    side:        str          = "LONG"   # "LONG" | "SHORT"
    created_at:  str          = field(default_factory=lambda: datetime.now().isoformat())
    order_id:    Optional[str] = None

    def __post_init__(self):
        if self.order_id is None:
            self.order_id = f"ORD-{int(time.time()*1000)}-{self.ticker}"


@dataclass
class Fill:
    order_id:    str
    ticker:      str
    action:      str
    qty:         int
    fill_price:  float
    commission:  float
    slippage:    float
    filled_at:   str  = field(default_factory=lambda: datetime.now().isoformat())
    status:      str  = "FILLED"


@dataclass
class ExecutionResult:
    fills:      List[Fill]   = field(default_factory=list)
    orders:     List[Order]  = field(default_factory=list)
    rejected:   List[Order]  = field(default_factory=list)
    total_cost: float        = 0.0
    total_notional: float    = 0.0
    success:    bool         = False
    mode:       str          = "paper"


# ══════════════════════════════════════════════════════
#  PAPER TRADING ENGINE
# ══════════════════════════════════════════════════════

class PaperTradingEngine:
    """
    Simulation réaliste du paper trading.

    Modélise :
      - Slippage (market impact proportionnel à la taille)
      - Commission (taux fixe par trade)
      - Latence simulée (pour réalisme)
      - Bid/Ask spread
      - Rejection partielle si liquidité insuffisante
    """

    def __init__(
        self,
        commission_bps:   float = 3.0,    # 3 bps par transaction
        slippage_bps:     float = 5.0,    # 5 bps slippage moyen
        slippage_std_bps: float = 2.0,    # variabilité du slippage
        bid_ask_bps:      float = 4.0,    # spread bid/ask moyen
        latency_ms:       float = 50.0,   # latence simulée (ms)
        reject_prob:      float = 0.01,   # probabilité de rejet (1%)
    ):
        self.commission_rate  = commission_bps  / 10_000
        self.slippage_rate    = slippage_bps    / 10_000
        self.slippage_std     = slippage_std_bps / 10_000
        self.bid_ask_rate     = bid_ask_bps     / 10_000
        self.latency_ms       = latency_ms
        self.reject_prob      = reject_prob

        self._positions: Dict[str, int]    = {}
        self._fills:     List[Fill]        = []
        self._cash:      float             = 0.0

    def _simulate_fill_price(
        self,
        ref_price:  float,
        action:     str,
        qty:        int,
        order_type: str,
        limit_price: Optional[float],
    ) -> Optional[float]:
        """
        Simule le prix d'exécution avec slippage et spread.
        Retourne None si l'ordre est rejeté.
        """
        if random.random() < self.reject_prob:
            return None   # rejet aléatoire

        # Spread bid/ask
        half_spread = ref_price * self.bid_ask_rate / 2
        if action == "BUY":
            base_price = ref_price + half_spread   # on achète à l'ask
        else:
            base_price = ref_price - half_spread   # on vend au bid

        # Slippage (log-normal positif dans le sens défavorable)
        slippage = abs(np.random.normal(self.slippage_rate, self.slippage_std))
        if action == "BUY":
            fill_price = base_price * (1 + slippage)
        else:
            fill_price = base_price * (1 - slippage)

        # Vérification limite
        if order_type == "LIMIT" and limit_price is not None:
            if action == "BUY"  and fill_price > limit_price:
                return None   # non exécuté (prix trop haut)
            if action == "SELL" and fill_price < limit_price:
                return None   # non exécuté (prix trop bas)

        return round(fill_price, 2)

    def execute_order(
        self,
        order:     Order,
        ref_price: float,
    ) -> Optional[Fill]:
        """
        Exécute un ordre en paper trading.

        Args:
            order:     Ordre à exécuter
            ref_price: Prix de référence (dernier cours connu)

        Returns:
            Fill si exécuté, None si rejeté
        """
        # Latence simulée
        time.sleep(self.latency_ms / 1000)

        fill_price = self._simulate_fill_price(
            ref_price, order.action, order.qty,
            order.order_type, order.limit_price,
        )

        if fill_price is None:
            logger.warning(f"Ordre rejeté : {order.order_id} ({order.ticker})")
            return None

        notional   = order.qty * fill_price
        commission = notional * self.commission_rate
        slippage   = abs(fill_price - ref_price) * order.qty

        fill = Fill(
            order_id   = order.order_id,
            ticker     = order.ticker,
            action     = order.action,
            qty        = order.qty,
            fill_price = fill_price,
            commission = round(commission, 2),
            slippage   = round(slippage, 2),
        )

        # Mise à jour position
        sign = 1 if order.action == "BUY" else -1
        self._positions[order.ticker] = (
            self._positions.get(order.ticker, 0) + sign * order.qty
        )
        self._fills.append(fill)

        logger.info(
            f"Fill: {order.action} {order.qty} × {order.ticker} "
            f"@ ¥{fill_price:,.0f} | comm ¥{commission:.0f} | "
            f"slip ¥{slippage:.0f}"
        )
        return fill

    def execute_portfolio(
        self,
        orders: List[Order],
        prices: Dict[str, float],
    ) -> ExecutionResult:
        """Exécute un portefeuille d'ordres complet."""
        result = ExecutionResult(mode="paper", orders=orders)

        for order in orders:
            ref = prices.get(order.ticker)
            if ref is None or ref <= 0:
                logger.warning(f"Prix absent pour {order.ticker} — ordre rejeté")
                result.rejected.append(order)
                continue

            fill = self.execute_order(order, ref)
            if fill:
                result.fills.append(fill)
                result.total_cost     += fill.commission + fill.slippage
                result.total_notional += fill.fill_price * fill.qty
            else:
                result.rejected.append(order)

        result.success = len(result.fills) > 0
        logger.info(
            f"Exécution terminée: {len(result.fills)} fills / "
            f"{len(result.rejected)} rejetés | "
            f"Coût total ¥{result.total_cost:,.0f}"
        )
        return result

    def get_positions(self) -> Dict[str, int]:
        return {t: q for t, q in self._positions.items() if q != 0}

    def get_fills_df(self):
        import pandas as pd
        if not self._fills:
            return pd.DataFrame()
        return pd.DataFrame([vars(f) for f in self._fills])


# ══════════════════════════════════════════════════════
#  LIVE IBKR ENGINE
# ══════════════════════════════════════════════════════

class IBKRExecutionEngine:
    """
    Exécution live via IBKR TWS.
    Enveloppe le provider IBKR pour la soumission d'ordres réels.
    """

    def __init__(self, ibkr_provider):
        self.provider = ibkr_provider

    def _make_ibkr_order(self, order: Order):
        from ib_insync import MarketOrder, LimitOrder
        if order.order_type == "LIMIT" and order.limit_price:
            return LimitOrder(order.action, order.qty, order.limit_price)
        return MarketOrder(order.action, order.qty)

    def execute_order(self, order: Order) -> Optional[Fill]:
        if not self.provider.is_connected():
            logger.error("IBKR non connecté — impossible d'exécuter l'ordre")
            return None
        try:
            contract   = self.provider._make_contract(order.ticker)
            ib_order   = self._make_ibkr_order(order)
            ib         = self.provider._ib
            ib.qualifyContracts(contract)
            trade      = ib.placeOrder(contract, ib_order)
            ib.sleep(2)   # attendre confirmation

            fill_price = trade.orderStatus.avgFillPrice
            filled_qty = int(trade.orderStatus.filled)

            if filled_qty == 0:
                logger.warning(f"Ordre non rempli : {order.order_id}")
                return None

            fill = Fill(
                order_id   = order.order_id,
                ticker     = order.ticker,
                action     = order.action,
                qty        = filled_qty,
                fill_price = fill_price,
                commission = 0.0,   # récupéré via execution report
                slippage   = 0.0,
                status     = trade.orderStatus.status,
            )
            logger.info(f"Fill IBKR: {order.action} {filled_qty} × {order.ticker} @ {fill_price}")
            return fill

        except Exception as e:
            logger.error(f"IBKR execute_order échoué : {e}")
            return None

    def cancel_all(self):
        """Annule tous les ordres ouverts."""
        try:
            self.provider._ib.reqGlobalCancel()
            logger.info("Tous les ordres annulés")
        except Exception as e:
            logger.error(f"cancel_all échoué : {e}")


# ══════════════════════════════════════════════════════
#  FACTORY
# ══════════════════════════════════════════════════════

def get_execution_engine(
    mode:            str = "paper",
    ibkr_provider    = None,
    commission_bps:  float = 3.0,
    slippage_bps:    float = 5.0,
):
    """
    Retourne le moteur d'exécution adapté au mode.

    Args:
        mode:           "paper" ou "live"
        ibkr_provider:  Instance IBKRDataProvider (requis en mode live)
    """
    if mode == "live":
        if ibkr_provider is None:
            raise ValueError("ibkr_provider requis en mode live")
        return IBKRExecutionEngine(ibkr_provider)
    else:
        return PaperTradingEngine(
            commission_bps=commission_bps,
            slippage_bps=slippage_bps,
        )