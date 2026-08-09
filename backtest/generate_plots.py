"""
📈 Professional Performance Plot Generator — PEAD S&P 500
================================================================================
This script runs the full backtest locally (requires model.py and raw data)
and generates an institutional-grade dual plot (Equity Curve & Drawdowns).
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

# Local folder imports fallback
sys.path.append(os.path.dirname(__file__))
from portfolio_engine import run_custom_portfolio_backtest

ORIGINAL_MODEL_DIR = r"C:\Users\DELL\Desktop\PHD\Expoloration\Lab\PST_012_pead_surprise_strategy\500SP\2_model"
sys.path.append(ORIGINAL_MODEL_DIR)

try:
    from model import PEADSurpriseStrategy
except ImportError:
    try:
        from model import PEADSurpriseStrategy
    except ImportError:
        PEADSurpriseStrategy = None


def generate_plots():
    if PEADSurpriseStrategy is None:
        print("ERROR: PEADSurpriseStrategy (model.py) not found.")
        print("Please run this script on your workspace machine where the original model code is available.")
        sys.exit(1)

    print("Initializing backtest and loading pricing datasets...")
    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    if not os.path.exists(price_data_path):
        print(f"ERROR: Pricing data not found at: {price_data_path}")
        sys.exit(1)

    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])
    # Exclude 2020 (atypical COVID structural break)
    df_data = df_data[df_data["Date"].dt.year != 2020].reset_index(drop=True)

    # Retrieve parameters for Variant 6
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(ORIGINAL_MODEL_DIR, "config.yaml")
    
    base_params = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_params = yaml.safe_load(f).get("parameters", {})

    # Parameters for Variant 6 (Holding 10d, SUE 1.5, Vol 1.5, SL 5%)
    params = base_params.copy()
    params.update({
        "sue_threshold": 1.5,
        "vol_expansion_threshold": 1.5,
        "holding_period": 10,
        "stop_loss": 0.05
    })

    print("Generating strategy trading signals...")
    strategy = PEADSurpriseStrategy()
    df_signals = strategy.predict(df_data, params=params)

    # Filter for Out-of-Sample (OOS) period 2021-2026
    cutoff = "2020-12-31"
    
    # 1. Backtest PEAD (OOS)
    df_data_oos = df_data[df_data["Date"] > cutoff].copy()
    df_signals_oos = df_signals.loc[df_data_oos.index].copy()
    
    print("Running OOS backtest (PEAD Variant 6)...")
    res_pead = run_custom_portfolio_backtest(df_data_oos, df_signals_oos, initial_capital=100000.0, cost_bps=4.0)
    
    # 2. Backtest Benchmark Buy & Hold
    print("Running OOS backtest (S&P 500 Buy & Hold)...")
    df_signals_bh = pd.Series(1.0, index=df_data_oos.index)
    res_bh = run_custom_portfolio_backtest(df_data_oos, df_signals_bh, initial_capital=100000.0, cost_bps=0.0)

    # Compute normalized equity curves to base 100
    pead_equity = (res_pead["equity_curve"] / 100000.0) * 100.0
    bh_equity = (res_bh["equity_curve"] / 100000.0) * 100.0

    # Compute Drawdowns
    pead_dd = (pead_equity - pead_equity.cummax()) / pead_equity.cummax() * 100.0
    bh_dd = (bh_equity - bh_equity.cummax()) / bh_equity.cummax() * 100.0

    # Plot creation
    print("Plotting performance curves...")
    sns.set_theme(style="darkgrid")
    
    # Colors
    color_pead = "#0F9D58"  # Quant Green
    color_bh = "#4285F4"    # Benchmark Blue
    color_dd = "#DB4437"    # Drawdown Red

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1.2]})

    # 1. Equity Curve (Log scale)
    ax1.plot(pead_equity.index, pead_equity.values, label=f"PEAD-Surprise (OOS Sharpe: {res_pead['metrics']['sharpe_ratio']:.3f})", color=color_pead, linewidth=2.5)
    ax1.plot(bh_equity.index, bh_equity.values, label=f"S&P 500 Buy & Hold (OOS Sharpe: {res_bh['metrics']['sharpe_ratio']:.3f})", color=color_bh, linewidth=1.5, linestyle="--")
    
    ax1.set_yscale('log')
    ax1.set_title("Out-of-Sample (OOS) Performance — 2021-2026\nPEAD-Surprise Strategy vs. S&P 500 Index (Net Frictions: 4.0 bps / trade)", fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel("Indexed Capital (Base 100 - Log Scale)", fontsize=12)
    ax1.legend(loc="upper left", fontsize=11, frameon=True)
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Format Y axis tickers
    import matplotlib.ticker as ticker
    ax1.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    # 2. Drawdown Plot
    ax2.fill_between(pead_dd.index, pead_dd.values, 0, label="PEAD Drawdown", color=color_pead, alpha=0.4)
    ax2.fill_between(bh_dd.index, bh_dd.values, 0, label="S&P 500 Drawdown", color=color_bh, alpha=0.2)
    
    ax2.set_ylabel("Drawdown (%)", fontsize=12)
    ax2.set_ylim(-60, 2)
    ax2.legend(loc="lower left", fontsize=10)
    ax2.grid(True, ls="--", alpha=0.5)

    # Final adjustments
    plt.tight_layout()
    
    # Save to assets directory
    assets_dir = os.path.join(local_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    out_img_path = os.path.join(assets_dir, "pead_performance.png")
    
    plt.savefig(out_img_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"SUCCESS: Performance chart saved successfully to: {out_img_path}")


if __name__ == "__main__":
    generate_plots()
