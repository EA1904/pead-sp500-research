"""
📊 3D Optimization Surface Generator — PEAD S&P 500
================================================================================
This script runs a grid search on key parameters (SUE threshold and holding period)
and generates a professional 3D performance surface chart.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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


def generate_3d_surface():
    if PEADSurpriseStrategy is None:
        print("ERROR: PEADSurpriseStrategy (model.py) not found.")
        sys.exit(1)

    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    if not os.path.exists(price_data_path):
        print(f"ERROR: Data not found at: {price_data_path}")
        sys.exit(1)

    print("Loading data for 3D analysis...")
    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])
    # Exclude 2020 (atypical COVID structural break)
    df_data = df_data[df_data["Date"].dt.year != 2020].reset_index(drop=True)

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

    # Parameter grid definition
    sue_thresholds = np.array([0.8, 1.2, 1.6, 2.0])
    holding_periods = np.array([5, 10, 15, 20, 25])

    # Matrices for 3D plotting
    SUE_grid, HOLD_grid = np.meshgrid(sue_thresholds, holding_periods)
    SHARPE_grid = np.zeros_like(SUE_grid, dtype=float)
    RETURN_grid = np.zeros_like(SUE_grid, dtype=float)

    print(f"Running grid optimization ({SUE_grid.size} backtests)...")
    for i in range(holding_periods.size):
        for j in range(sue_thresholds.size):
            sue = sue_thresholds[j]
            hold = holding_periods[i]
            
            print(f"  Simulation : SUE={sue:.1f} | Holding={hold} days...")
            
            params = base_params.copy()
            params.update({
                "sue_threshold": sue,
                "vol_expansion_threshold": 1.5,
                "holding_period": int(hold),
                "stop_loss": 0.05
            })
            
            df_sig = strategy.predict(df_data_oos, params=params)
            res = run_custom_portfolio_backtest(df_data_oos, df_sig, initial_capital=100000.0, cost_bps=4.0)
            
            SHARPE_grid[i, j] = res["metrics"]["sharpe_ratio"]
            RETURN_grid[i, j] = res["metrics"]["annualized_return"] * 100.0

    print("Generating 3D plot...")
    
    # Styling
    sns.set_theme(style="white")
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Plot surface
    surf = ax.plot_surface(
        SUE_grid, 
        HOLD_grid, 
        SHARPE_grid, 
        cmap='viridis',
        edgecolor='none', 
        alpha=0.9,
        antialiased=True,
        rstride=1,
        cstride=1
    )

    # Projected contour curves at the bottom
    cset = ax.contour(
        SUE_grid, 
        HOLD_grid, 
        SHARPE_grid, 
        zdir='z', 
        offset=SHARPE_grid.min() - 0.2, 
        cmap='viridis',
        alpha=0.5
    )

    # Label styling
    ax.set_xlabel('SUE Threshold (Surprise)', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel('Holding Period (Days)', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_zlabel('Sharpe Ratio (OOS)', fontsize=11, fontweight='bold', labelpad=10)
    
    # Adjust Z limits to fit contours
    ax.set_zlim(SHARPE_grid.min() - 0.2, SHARPE_grid.max() + 0.2)

    # Set view angle
    ax.view_init(elev=25, azim=-135)

    # Colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
    cbar.set_label('Annualized Sharpe Ratio', fontsize=10, fontweight='bold')

    plt.title("PEAD Parameter Optimization Surface (3D)\nOut-of-Sample Sharpe Ratio (2021-2026) vs. SUE Threshold & Holding Period", fontsize=14, fontweight='bold', pad=20)

    # Save
    plt.tight_layout()
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_path = os.path.join(local_dir, "assets", "pead_parameter_surface.png")
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"SUCCESS: 3D Parameter Surface saved successfully to: {out_path}")


if __name__ == "__main__":
    generate_3d_surface()



if __name__ == "__main__":
    generate_3d_surface()
