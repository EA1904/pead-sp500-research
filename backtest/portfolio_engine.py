import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(__file__))
from metrics import calculate_metrics


def run_custom_portfolio_backtest(df_data, df_signals, initial_capital=100000.0, cost_bps=4.0):
    """
    Construit l'equity curve d'un portefeuille equal-weight de manière vectorisée
    en n'allouant le capital qu'aux positions actives (signal != 0).
    Les tickers avec signal=0 ne consomment PAS de capital.
    """
    df = df_data[["Date", "Ticker", "Close"]].copy()
    df["Signal"] = df_signals.values
    df["Date"] = pd.to_datetime(df["Date"])

    # Assurer le tri
    df = df.sort_values(["Date", "Ticker"]).reset_index(drop=True)

    # Pivoter les cours et les signaux pour vectorisation
    df_pivot = df.pivot(index="Date", columns="Ticker", values=["Close", "Signal"])
    close = df_pivot["Close"]
    signal = df_pivot["Signal"].fillna(0.0)

    # Rendements journaliers par ticker
    returns = close.pct_change().fillna(0.0)

    # Changements de position pour les frais de transaction
    prev_signal = signal.shift(1).fillna(0.0)
    traded = (signal != prev_signal).astype(float)

    # Compter le nombre de positions actives chaque jour
    n_active = (signal != 0).sum(axis=1)

    # Déterminer les poids par ticker (1 / n_active si actif, sinon 0)
    n_active_safe = n_active.replace(0, 1)
    weights = pd.DataFrame(0.0, index=signal.index, columns=signal.columns)
    for col in signal.columns:
        weights[col] = np.where(signal[col] != 0, 1.0 / n_active_safe, 0.0)

    # Rendement brut journalier du portefeuille
    port_rets_raw = (signal * weights * returns).sum(axis=1)

    # Coûts de transaction journaliers
    cost_fraction = cost_bps / 10000.0
    daily_costs = (traded * weights * cost_fraction).sum(axis=1)

    # Rendement net journalier
    daily_net_rets = port_rets_raw - daily_costs

    # Reconstruction de la courbe de capital cumulé
    equity = [initial_capital]
    for r in daily_net_rets.values[1:]:
        equity.append(equity[-1] * (1.0 + r))

    equity_curve = pd.Series(equity, index=close.index)

    # Extraire les trades par ticker pour le calcul des métriques
    df["Prev_Signal"] = df.groupby("Ticker")["Signal"].shift(1).fillna(0.0)
    trades_df = _extract_portfolio_trades(df)

    metrics = calculate_metrics(equity_curve, trades_df)
    return {"equity_curve": equity_curve, "trades": trades_df, "metrics": metrics}


def _extract_portfolio_trades(df):
    """Extrait les trades (entrée/sortie) par ticker à partir des signaux en utilisant numpy."""
    trades = []
    
    # Tri préalable pour garantir l'ordre temporel dans le groupby
    df_sorted = df.sort_values(["Ticker", "Date"])
    
    for ticker, tdf in df_sorted.groupby("Ticker", sort=False):
        # Optimisation : ignorer les tickers qui n'ont jamais de signal actif
        if not (tdf["Signal"] != 0).any() and not (tdf["Prev_Signal"] != 0).any():
            continue
            
        dates = tdf["Date"].values
        closes = tdf["Close"].values
        signals = tdf["Signal"].values
        prev_signals = tdf["Prev_Signal"].values

        active_trade = None
        for i in range(len(tdf)):
            sig = signals[i]
            prev = prev_signals[i]
            if sig != prev:
                # Fermer le trade actif
                if active_trade is not None:
                    active_trade["exit_date"] = dates[i]
                    active_trade["exit_price"] = closes[i]
                    ep, xp = active_trade["entry_price"], active_trade["exit_price"]
                    d = active_trade["direction"]
                    active_trade["pnl_pct"] = (xp - ep) / ep if d == 1 else (ep - xp) / ep
                    active_trade["duration_days"] = (pd.to_datetime(active_trade["exit_date"]) - pd.to_datetime(active_trade["entry_date"])).days
                    trades.append(active_trade)
                    active_trade = None
                # Ouvrir un nouveau trade
                if sig != 0:
                    active_trade = {
                        "entry_date": dates[i], "direction": int(sig),
                        "entry_price": closes[i], "exit_date": None,
                        "exit_price": None, "pnl_pct": 0.0, "duration_days": 0,
                        "ticker": ticker
                    }
        # Fermer le trade restant
        if active_trade is not None:
            active_trade["exit_date"] = dates[-1]
            active_trade["exit_price"] = closes[-1]
            ep, xp = active_trade["entry_price"], active_trade["exit_price"]
            d = active_trade["direction"]
            active_trade["pnl_pct"] = (xp - ep) / ep if d == 1 else (ep - xp) / ep
            active_trade["duration_days"] = (pd.to_datetime(active_trade["exit_date"]) - pd.to_datetime(active_trade["entry_date"])).days
            trades.append(active_trade)

    return pd.DataFrame(trades) if trades else pd.DataFrame()
