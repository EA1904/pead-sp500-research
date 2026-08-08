"""
📊 Academic Plot Generator for GAT Multiplex & Permutation Tests
================================================================================
Generates high-resolution, institutional-grade visual assets for the GAT extension,
including the performance comparison chart, the permutation test chart, and the 
transaction cost sensitivity chart, directly from the paper's verified data.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def generate_gat_charts():
    # Setup aesthetic style
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'font.sans-serif': 'sans-serif',
        'axes.unicode_minus': False,
        'figure.titlesize': 14,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10
    })
    
    # Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)
    
    # --------------------------------------------------------------------------
    # CHART 1: GAT Model Performance Comparison (Sharpe Ratio)
    # --------------------------------------------------------------------------
    print("Generating GAT performance comparison chart...")
    strategies = [
        "S&P 500 Buy & Hold",
        "Naive Post-Earnings Buy",
        "Classical PEAD (Baseline)",
        "GAT Multiplex (Long-Only)",
        "GAT Multiplex (Long-Short)",
        "GAT Multiplex (Sector Filtered)"
    ]
    sharpes = [0.855, 0.745, 2.131, 2.180, 2.240, 2.326]
    returns = [14.41, 15.28, 77.73, 79.15, 80.50, 81.88]
    
    df_perf = pd.DataFrame({
        "Strategy": strategies,
        "Sharpe": sharpes,
        "Return": returns
    })
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    # Color palette matching premium academic theme
    colors = [
        "#7F8C8D", # Grey (B&H)
        "#95A5A6", # Light Grey (Naive)
        "#4285F4", # Blue (Classical)
        "#34A853", # Green (GAT LO)
        "#2ECC71", # Light Green (GAT LS)
        "#0F9D58"  # Dark Green (GAT Sector Filtered - Optimal)
    ]
    
    bars = ax.barh(df_perf["Strategy"], df_perf["Sharpe"], color=colors, height=0.6, edgecolor='none')
    
    # Add metrics text labels on top of the bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ret = df_perf.iloc[i]["Return"]
        ax.text(
            width + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"Sharpe: {width:.3f} | Ann. Return: {ret:.2f}%",
            va='center',
            ha='left',
            fontweight='bold',
            fontsize=10,
            color="#2C3E50"
        )
        
    ax.set_title("Out-of-Sample Performance Comparison (OOS 2021-2026)\nNet of Frictions (4.0 bps) | T+1 Open Execution", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Annualized Sharpe Ratio", fontsize=11, fontweight='bold')
    ax.set_xlim(0, max(sharpes) + 0.6)
    ax.xaxis.grid(True, linestyle="--", alpha=0.6)
    ax.yaxis.grid(False)
    
    # Despine
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "gat_performance_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # CHART 2: GNN Permutation Test (Topology vs. Weights)
    # --------------------------------------------------------------------------
    print("Generating GNN permutation test chart...")
    models = [
        "No-Graph PEAD Baseline",
        "Random-Init GAT\n(Average of 10 Runs)",
        "Trained Multiplex GAT\n(Optimal K=4)"
    ]
    perm_sharpes = [1.811, 2.249, 2.259]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bar_colors = ["#4285F4", "#E74C3C", "#0F9D58"]
    bars_perm = ax.bar(models, perm_sharpes, color=bar_colors, width=0.5, edgecolor='none')
    
    # Add values on top of the bars
    for bar in bars_perm:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"Sharpe: {height:.3f}",
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=10,
            color="#2C3E50"
        )
        
    # Draw double headed arrow showing topological gain
    ax.annotate(
        '', xy=(1, 2.15), xytext=(0, 1.85),
        arrowprops=dict(arrowstyle="<->", color="#2C3E50", lw=1.5, ls="--")
    )
    ax.text(0.5, 2.05, "Topological Gain\n+0.438 Sharpe", ha='center', va='center', fontsize=9, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))
    
    # Draw arrow showing training gain
    ax.annotate(
        '', xy=(2, 2.259), xytext=(1, 2.249),
        arrowprops=dict(arrowstyle="->", color="#E74C3C", lw=1.2)
    )
    ax.text(1.5, 2.30, "Training Gain\n+0.010 Sharpe\n(p = 0.30, n.s.)", ha='center', va='center', fontsize=9, color="#E74C3C")

    ax.set_title("GNN Permutation Test: Network Topology vs. Learned Weights\nAblation Backtesting Configuration (2021-2026)", fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel("Annualized Sharpe Ratio", fontsize=11, fontweight='bold')
    ax.set_ylim(0, 2.6)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6)
    ax.xaxis.grid(False)
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "gnn_permutation_test.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # CHART 3: Transaction Cost Sensitivity (Friction Stress Test)
    # --------------------------------------------------------------------------
    print("Generating transaction cost sensitivity chart...")
    frictions = [0, 4, 10, 20, 30, 50]
    sharpe_sens = [2.410, 2.326, 2.180, 1.850, 1.480, 0.950]
    
    fig, ax = plt.subplots(figsize=(8.5, 5))
    
    ax.plot(frictions, sharpe_sens, marker='o', linewidth=2.5, color="#0F9D58", label="OOS Sharpe Ratio")
    
    # Annotate points
    for x, y in zip(frictions, sharpe_sens):
        ax.annotate(
            f"{y:.3f}",
            xy=(x, y),
            xytext=(0, 8),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=9,
            color="#2C3E50"
        )
        
    # Shading the institutional spread region
    ax.axvspan(2, 5, color='#F1C40F', alpha=0.2, label="Institutional Spread (2-5 bps)")
    
    # Annotate 4 bps baseline
    ax.annotate(
        "Baseline Model (4.0 bps)\nSharpe = 2.326",
        xy=(4, 2.326),
        xytext=(15, 20),
        textcoords='offset points',
        arrowprops=dict(facecolor='#2C3E50', arrowstyle="->"),
        fontweight='bold',
        fontsize=9,
        color="#2C3E50"
    )

    ax.set_title("Transaction Cost Sensitivity & Friction Stress Test\nGAT Multiplex (Sector Filtered) - Out-of-Sample (2021-2026)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Round-Trip Transaction Cost / Slippage (bps)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Annualized Sharpe Ratio", fontsize=11, fontweight='bold')
    ax.set_xlim(-2, 55)
    ax.set_ylim(0.5, 2.7)
    ax.legend(loc="lower left", frameon=True, fontsize=10)
    
    ax.grid(True, linestyle="--", alpha=0.6)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "friction_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("SUCCESS: All GAT academic charts generated successfully in assets/!")

if __name__ == "__main__":
    generate_gat_charts()
