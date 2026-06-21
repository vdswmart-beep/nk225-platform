#!/usr/bin/env python
# run.py — Pipeline headless : backtest + track record + export Excel
#
# Usage :
#   python run.py                          # backtest standard
#   python run.py --mode backtest          # identique
#   python run.py --mode walkforward       # walk-forward complet
#   python run.py --universe liquid40      # 40 tickers
#   python run.py --universe full          # 185 tickers Nikkei 225
#   python run.py --export-excel           # génère le track record Excel

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/run.log", mode="a"),
    ],
)
logger = logging.getLogger("run")


def parse_args():
    p = argparse.ArgumentParser(description="NK225 — Pipeline headless")
    p.add_argument("--mode",         default="backtest",
                   choices=["backtest", "walkforward", "live"])
    p.add_argument("--universe",     default="default",
                   choices=["default", "liquid40", "full"])
    p.add_argument("--start",        default="2022-01-01")
    p.add_argument("--end",          default="2026-01-01")
    p.add_argument("--train-months", type=int, default=12)
    p.add_argument("--test-months",  type=int, default=3)
    p.add_argument("--method",       default="risk_parity",
                   choices=["risk_parity", "hrp", "mean_variance", "equal_weight"])
    p.add_argument("--export-excel", action="store_true",
                   help="Génère le track record Excel après le backtest")
    p.add_argument("--output-dir",   default="outputs")
    return p.parse_args()


def run_standard_pipeline(args, tickers, ds):
    """Pipeline one-shot (backtest unique)."""
    from config.settings import DEFAULT_METHOD
    from pipelines.master_pipeline import MasterPipeline

    pipeline = MasterPipeline(
        data_service      = ds,
        tickers           = tickers,
        start             = args.start,
        end               = args.end,
        market_regime     = "neutral",
        portfolio_method  = args.method or DEFAULT_METHOD,
        mode              = "backtest",
    )
    out = pipeline.run()

    if out.success:
        logger.info("━" * 60)
        logger.info("RÉSULTATS PIPELINE")
        logger.info(f"  Longs  : {len(out.ideas.longs)}")
        logger.info(f"  Shorts : {len(out.ideas.shorts)}")
        logger.info(f"  VaR    : {out.risk.var * 100:.2f}%")
        logger.info(f"  Sharpe : {out.risk.sharpe:.2f}")
        logger.info(f"  MaxDD  : {out.risk.max_drawdown * 100:.2f}%")
        logger.info("━" * 60)

        if args.export_excel:
            _export_simple(out, args)
    else:
        logger.error("Pipeline échoué")
        sys.exit(1)

    return out


def run_walkforward(args, tickers, ds):
    """Walk-forward backtest avec export complet."""
    from backtesting.backtest_engine import BacktestEngine, momentum_pipeline

    logger.info("▶ Walk-forward backtest démarré")
    logger.info(f"  Train : {args.train_months}M | Test : {args.test_months}M")

    # Chargement des rendements
    returns = ds.get_returns(tickers, args.start, args.end)
    logger.info(f"  Returns shape : {returns.shape}")

    def pipeline_fn(ret):
        return momentum_pipeline(ret, top_n=max(3, len(ret.columns) // 5))

    engine = BacktestEngine(
        train_months=args.train_months,
        test_months=args.test_months,
        slippage_bps=5.0,
        cost_bps=3.0,
    )
    result = engine.run(returns, pipeline_fn)

    # Affichage résultats
    m = result.metrics
    logger.info("━" * 60)
    logger.info("RÉSULTATS WALK-FORWARD")
    logger.info(f"  Fenêtres    : {len(result.windows)}")
    logger.info(f"  Total Return: {m.get('total_return', 0):.2%}")
    logger.info(f"  Ann. Return : {m.get('ann_return', 0):.2%}")
    logger.info(f"  Volatilité  : {m.get('ann_vol', 0):.2%}")
    logger.info(f"  Sharpe      : {m.get('sharpe', 0):.3f}")
    logger.info(f"  Sortino     : {m.get('sortino', 0):.3f}")
    logger.info(f"  Max DrawDown: {m.get('max_drawdown', 0):.2%}")
    logger.info(f"  Win Rate    : {m.get('win_rate', 0):.2%}")
    logger.info(f"  Profit Factor:{m.get('profit_factor', 0):.2f}")
    logger.info(f"  VaR 95%     : {m.get('var_95', 0):.2%}")
    logger.info("━" * 60)

    if args.export_excel:
        from reporting.excel_exporter import export_track_record
        from datetime import datetime
        date_str  = datetime.now().strftime("%Y%m%d_%H%M")
        out_path  = Path(args.output_dir) / f"track_record_{date_str}.xlsx"
        saved     = export_track_record(result, output_path=str(out_path))
        logger.info(f"✓ Track record Excel → {saved}")

    return result


def _export_simple(pipeline_out, args):
    """Export Excel simplifié depuis un run standard."""
    try:
        from reporting.track_record import TrackRecord
        tr = TrackRecord(outputs_dir=args.output_dir)
        for idea in pipeline_out.ideas.longs[:5]:
            tr.log_trade(
                ticker=idea["ticker"],
                action="BUY",
                qty=0,
                price=0,
                weight=pipeline_out.portfolio.weights.get(idea["ticker"], 0),
                side="LONG",
            )
        for idea in pipeline_out.ideas.shorts[:5]:
            tr.log_trade(
                ticker=idea["ticker"],
                action="SELL",
                qty=0,
                price=0,
                weight=pipeline_out.portfolio.weights.get(idea["ticker"], 0),
                side="SHORT",
            )
        logger.info(f"✓ Track record mis à jour → {args.output_dir}/")
    except Exception as e:
        logger.warning(f"Export Excel échoué (non bloquant) : {e}")


def main():
    args = parse_args()

    # Univers
    from config.universe import get_universe
    tickers = get_universe(args.universe)
    logger.info(f"Univers : {args.universe} → {len(tickers)} tickers")
    logger.info(f"Période : {args.start} → {args.end}")

    # DataService
    from data.data_service import DataService
    ds = DataService(mode="backtest")

    if args.mode == "walkforward":
        run_walkforward(args, tickers, ds)
    else:
        run_standard_pipeline(args, tickers, ds)


if __name__ == "__main__":
    main()