"""
📊 Signal Variant & Benchmark Comparison Chart Generator — PEAD S&P 500
================================================================================
This script runs backtests for the 6 variants of the PEAD strategy as well as
the Buy & Hold benchmark on the Out-of-Sample (OOS) period, then generates a
premium horizontal bar chart comparing their Sharpe ratios.
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


def generate_comparison():
    if PEADSurpriseStrategy is None:
        print("ERROR: PEADSurpriseStrategy (model.py) not found.")
        sys.exit(1)

    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    if not os.path.exists(price_data_path):
        print(f"ERROR: Data not found at: {price_data_path}")
        sys.exit(1)

    print("Loading data for comparison chart...")
    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])

    # Out-of-Sample (OOS) period
    cutoff = "2020-12-31"
    df_data_oos = df_data[df_data["Date"] > cutoff].copy()

    # Load parameters
    base_params = {}
    config_path = os.path.join(ORIGINAL_MODEL_DIR, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_params = yaml.safe_load(f).get("parameters", {})

    strategy = PEADSurpriseStrategy()

    variants = {
        "1) Baseline (SUE 1.5, Vol 1.5, SL 5%, 20d)": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "2) Aggressive SUE (SUE 1.0)": {
            "sue_threshold": 1.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "3) Conservative SUE (SUE 2.0)": {
            "sue_threshold": 2.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "4) Without Volume Filter": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 0.0, "holding_period": 20, "stop_loss": 0.05
        },
        "5) Without Stop Loss": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 1.0
        },
        "6) Short Holding (10-Days) [OPTIMAL]": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 10, "stop_loss": 0.05
        },
        "S&P 500 Buy & Hold": {"is_bh": True}
    }

    results = []

    print("Executing backtests...")
    for name, vsettings in variants.items():
        print(f"  Simulating: {name}...")
        if vsettings.get("is_bh", False):
            df_sig = pd.Series(1.0, index=df_data_oos.index)
            res = run_custom_portfolio_backtest(df_data_oos, df_sig, initial_capital=100000.0, cost_bps=0.0)
        else:
            params = base_params.copy()
            params.update(vsettings)
            df_sig = strategy.predict(df_data_oos, params=params)
            res = run_custom_portfolio_backtest(df_data_oos, df_sig, initial_capital=100000.0, cost_bps=4.0)
        
        results.append({
            "Variant": name,
            "Sharpe": res["metrics"]["sharpe_ratio"],
            "Return": res["metrics"]["annualized_return"] * 100.0
        })

    df_res = pd.DataFrame(results)
    
    # Plotting
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Sort to show hierarchy
    df_sorted = df_res.sort_values("Sharpe", ascending=True)

    # Color palette
    colors = []
    for var in df_sorted["Variant"]:
        if "OPTIMAL" in var:
            colors.append("#0F9D58")  # Quant Green
        elif "Buy & Hold" in var:
            colors.append("#7F8C8D")  # Grey Benchmark
        else:
            colors.append("#4285F4")  # Standard Blue

    ax = sns.barplot(
        x="Sharpe", 
        y="Variant", 
        data=df_sorted, 
        palette=colors,
        hue="Variant",
        legend=False
    )

    # Add text labels on the bars
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        ax.text(
            width + 0.05, 
            p.get_y() + p.get_height() / 2, 
            f"SR: {width:.3f} | Ann. Ret: {df_sorted.iloc[i]['Return']:.1f}%", 
            ha="left", 
            va="center", 
            fontweight='bold', 
            fontsize=10
        )

    plt.title("PEAD Signal Variants & Benchmark Comparison (OOS Sharpe Ratio)\nOut-of-Sample Period: 2021-2026", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Annualized Sharpe Ratio", fontsize=11)
    plt.ylabel("")
    plt.xlim(0, df_res["Sharpe"].max() + 0.6)
    
    plt.tight_layout()

    # Save
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_path = os.path.join(local_dir, "assets", "pead_variants_comparison.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"SUCCESS: Comparison chart saved successfully to: {out_path}")


if __name__ == "__main__":
    generate_comparison()



if __name__ == "__main__":
    generate_comparison()
