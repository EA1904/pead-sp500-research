"""
📊 Modern Minimalist Plot Generator for GAT Multiplex & Permutation Tests
================================================================================
Generates high-resolution, Stripe/Vercel-style minimalist charts for the GAT 
extension, using lollipop plots, clean geometry, and modern typography.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def generate_gat_charts():
    # Setup premium minimalist style
    sns.set_theme(style="white")
    
    # Custom matplotlib configuration for modern look
    plt.rcParams.update({
        'font.sans-serif': 'Arial, Helvetica, sans-serif',
        'font.family': 'sans-serif',
        'axes.unicode_minus': False,
        'axes.edgecolor': '#E2E8F0',
        'axes.linewidth': 1,
        'grid.color': '#F1F5F9',
        'grid.linestyle': '--',
        'xtick.color': '#64748B',
        'ytick.color': '#64748B',
        'text.color': '#1E293B',
        'axes.labelcolor': '#475569'
    })
    
    # Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)
    
    # --------------------------------------------------------------------------
    # CHART 1: GAT Model Performance Comparison (Minimalist Horizontal Bars)
    # --------------------------------------------------------------------------
    print("Generating modern GAT performance comparison chart...")
    strategies = [
        "S&P 500 Buy & Hold",
        "Naive Post-Earnings Buy",
        "Classical PEAD (Baseline)",
        "GAT Multiplex (Long-Only)",
        "GAT Multiplex (Long-Short)",
        "GAT Multiplex (Sector Filtered)"
    ]
    sharpes = [0.855, 0.745, 2.131, 2.180, 2.240, 2.326]
    
    df_perf = pd.DataFrame({
        "Strategy": strategies,
        "Sharpe": sharpes
    })
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Clean, modern palette (Slate -> Indigo -> Teal)
    colors = [
        "#94A3B8",  # Slate 400
        "#CBD5E1",  # Slate 300
        "#6366F1",  # Indigo 500
        "#4F46E5",  # Indigo 600
        "#0D9488",  # Teal 600
        "#0F9D58"   # Emerald (Optimal)
    ]
    
    # Draw thin horizontal bars
    bars = ax.barh(df_perf["Strategy"], df_perf["Sharpe"], color=colors, height=0.45, zorder=2)
    
    # Add values clean and small at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.3f}",
            va='center',
            ha='left',
            fontweight='bold',
            fontsize=10,
            color="#475569"
        )
        
    ax.set_title("Out-of-Sample Performance Comparison (OOS 2021-2026)", fontsize=13, fontweight='bold', pad=15, loc='left', color="#0F172A")
    ax.set_xlabel("Annualized Sharpe Ratio", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_xlim(0, max(sharpes) + 0.3)
    ax.xaxis.grid(True, linestyle="--", alpha=0.7, color="#E2E8F0")
    ax.yaxis.grid(False)
    
    # Remove top and right spines, lighten others
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "gat_performance_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # CHART 2: GNN Permutation Test (Minimalist Lollipop Plot)
    # --------------------------------------------------------------------------
    print("Generating modern GNN permutation lollipop chart...")
    models = [
        "Classical PEAD\n(No Graph)",
        "Random GAT\n(Topology Only)",
        "Trained GAT\n(Topology + Weights)"
    ]
    perm_sharpes = [1.811, 2.249, 2.259]
    
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    # Lollipop lines
    ax.vlines(x=models, ymin=0, ymax=perm_sharpes, color="#E2E8F0", lw=2, zorder=1)
    
    # Lollipop dots
    dot_colors = ["#6366F1", "#8B5CF6", "#0F9D58"]
    dots = ax.scatter(models, perm_sharpes, color=dot_colors, s=350, zorder=3, edgecolors='none')
    
    # Add values centered inside the lollipop heads or cleanly above
    for i, val in enumerate(perm_sharpes):
        ax.text(
            i,
            val + 0.08,
            f"{val:.3f}",
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=10,
            color="#1E293B"
        )
        
    # Draw a clean vertical background span to highlight GNN performance increase
    ax.axhspan(1.811, 2.259, color='#0F9D58', alpha=0.04, zorder=0)
    
    # Highlight the topological gain with a clean textual label
    ax.text(
        0.5, 2.03, 
        "Topological Shift\n+0.438 Sharpe", 
        ha='center', 
        va='center', 
        fontsize=9, 
        fontweight='bold', 
        color="#0D9488",
        bbox=dict(facecolor='white', edgecolor='#0D9488', boxstyle='round,pad=0.5', lw=1)
    )
    
    # Show the negligible difference between random and trained weights
    ax.annotate(
        "No Weight Advantage\n+0.010 Sharpe (p = 0.30, n.s.)", 
        xy=(2, 2.259), 
        xytext=(1.05, 2.38),
        arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.2),
        fontsize=9, 
        fontweight='bold', 
        color="#64748B"
    )

    ax.set_title("GNN Permutation Test: Topology vs. Weights (OOS 2021-2026)", fontsize=13, fontweight='bold', pad=20, loc='left', color="#0F172A")
    ax.set_ylabel("Annualized Sharpe Ratio", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_ylim(0, 2.65)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, color="#E2E8F0")
    ax.xaxis.grid(False)
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "gnn_permutation_test.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # CHART 3: Transaction Cost Sensitivity (Minimalist Line Chart)
    # --------------------------------------------------------------------------
    print("Generating modern transaction cost sensitivity chart...")
    frictions = [0, 4, 10, 20, 30, 50]
    sharpe_sens = [2.410, 2.326, 2.180, 1.850, 1.480, 0.950]
    
    fig, ax = plt.subplots(figsize=(8.5, 5))
    
    # Shading the institutional spread region
    ax.axvspan(2, 5, color='#0D9488', alpha=0.06, label="Typical Institutional Spread (2-5 bps)")
    
    # Smooth line plot
    ax.plot(frictions, sharpe_sens, marker='o', markersize=6, linewidth=2, color="#0F9D58", label="OOS Sharpe Ratio", zorder=2)
    
    # Annotate points cleanly
    for x, y in zip(frictions, sharpe_sens):
        ax.annotate(
            f"{y:.2f}",
            xy=(x, y),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=9,
            color="#475569"
        )
        
    # Annotate 4 bps baseline
    ax.annotate(
        "Baseline Cost (4.0 bps)\nSharpe = 2.33",
        xy=(4, 2.326),
        xytext=(15, 20),
        textcoords='offset points',
        arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2),
        fontweight='bold',
        fontsize=9,
        color="#1E293B"
    )

    ax.set_title("Friction Sensitivity & Execution Cost Stress Test", fontsize=13, fontweight='bold', pad=15, loc='left', color="#0F172A")
    ax.set_xlabel("Round-Trip Transaction Cost / Slippage (bps)", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_ylabel("Annualized Sharpe Ratio", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_xlim(-2, 55)
    ax.set_ylim(0.5, 2.7)
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    
    ax.grid(True, linestyle="--", alpha=0.7, color="#E2E8F0")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "friction_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("SUCCESS: All modern minimalist GAT charts generated successfully in assets/!")

if __name__ == "__main__":
    generate_gat_charts()
