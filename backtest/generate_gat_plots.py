"""
📊 Premium Dark-Mode Chart Generator — PEAD + GAT Multiplex
================================================================================
Generates Bloomberg-terminal / Vercel-dashboard-style dark mode visuals:
  - Dark navy background (#0F172A)
  - Accent colors: Emerald, Indigo, Violet on dark surfaces
  - Tight Y axes (no dead space)
  - Clean typography, sharp annotations
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import numpy as np

# ────────────────────────────────────────────────────────────────────────────
# GLOBAL DARK THEME
# ────────────────────────────────────────────────────────────────────────────
BG        = "#0F172A"   # Slate-950 navy (background)
SURFACE   = "#1E293B"   # Slate-800  (card/surface)
BORDER    = "#334155"   # Slate-700  (axes edges)
TEXT_PRI  = "#F1F5F9"   # Slate-100  (primary text)
TEXT_SEC  = "#94A3B8"   # Slate-400  (secondary text)
GRID_COL  = "#1E293B"   # very subtle grid

EMERALD   = "#10B981"   # Optimal / positive
TEAL      = "#0D9488"   # Teal-600
INDIGO    = "#818CF8"   # Indigo-400
VIOLET    = "#A78BFA"   # Violet-400
SLATE     = "#64748B"   # Neutral benchmark
SLATE_LT  = "#94A3B8"   # Light neutral

def apply_dark_theme(fig, ax_list):
    fig.patch.set_facecolor(BG)
    for ax in ax_list if hasattr(ax_list, '__iter__') else [ax_list]:
        ax.set_facecolor(SURFACE)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
            spine.set_linewidth(0.8)
        ax.tick_params(colors=TEXT_SEC, labelsize=9)
        ax.xaxis.label.set_color(TEXT_SEC)
        ax.yaxis.label.set_color(TEXT_SEC)
        ax.grid(color=GRID_COL, linestyle='--', linewidth=0.7, alpha=0.9)


def set_title(ax, title, subtitle=None):
    """Left-aligned dual-line title with optional subtitle."""
    pad = 28 if subtitle else 12
    ax.set_title(title, loc='left', color=TEXT_PRI, fontsize=12,
                 fontweight='bold', pad=pad)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1.065), xycoords='axes fraction',
                    ha='left', va='bottom', color=TEXT_SEC, fontsize=8.2,
                    annotation_clip=False)


# ────────────────────────────────────────────────────────────────────────────
# CHART 1  ·  Performance Comparison — Horizontal Bars
# ────────────────────────────────────────────────────────────────────────────
def chart_performance():
    labels   = ["S&P 500 Buy & Hold",
                "Naive Post-Earnings",
                "Classical PEAD (Baseline)",
                "GAT Multiplex · Long-Only",
                "GAT Multiplex · Long-Short",
                "GAT Multiplex · Sector Filtered ★"]
    sharpes  = [0.855, 0.745, 2.131, 2.180, 2.240, 2.326]
    returns  = [14.41, 15.28, 77.73, 79.15, 80.50, 81.88]
    colors   = [SLATE, SLATE_LT, INDIGO, INDIGO, TEAL, EMERALD]
    alphas   = [0.55, 0.45, 0.75, 0.85, 0.90, 1.0]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    apply_dark_theme(fig, ax)

    y_pos = np.arange(len(labels))

    # Draw background highlight for GAT block
    ax.axhspan(2.4, 5.6, color=EMERALD, alpha=0.035, zorder=0)
    ax.axhline(y=2.35, color=BORDER, lw=0.8, linestyle='--', zorder=1)

    for i, (lbl, sh, ret, col, al) in enumerate(zip(labels, sharpes, returns, colors, alphas)):
        bar = ax.barh(i, sh, height=0.52, color=col, alpha=al, zorder=2,
                      left=0)

        # Value label inside bar (if bar wide enough) or outside
        x_lbl = sh - 0.08 if sh > 0.5 else sh + 0.04
        ha = 'right' if sh > 0.5 else 'left'
        ax.text(x_lbl, i, f"{sh:.3f}", va='center', ha=ha,
                color=TEXT_PRI, fontsize=9.5, fontweight='bold', zorder=3)

        # Ann. Return badge on the right margin
        ax.text(2.48, i, f"+{ret:.1f}%", va='center', ha='left',
                color=TEXT_SEC, fontsize=8.5)

    # Separator annotation between passive benchmarks and active strategies
    ax.text(-0.03, 1.65, "— Passive Benchmarks", color=SLATE, fontsize=7.5,
            style='italic', ha='left', va='center')
    ax.text(-0.03, 4.85, "— GAT Network-Augmented", color=TEAL, fontsize=7.5,
            style='italic', ha='left', va='center')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=TEXT_PRI, fontsize=9.5)
    ax.set_xlim(0, 2.55)
    ax.set_xlabel("Annualized Sharpe Ratio (OOS)", color=TEXT_SEC, fontsize=9.5)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)

    # Header
    set_title(ax, "Out-of-Sample Performance — OOS 2021–2026",
              "S&P 500 Universe (590 stocks) · T+1 Open Execution · 4.0 bps friction · Sharpe ratio comparison")

    # Ann. Return column header
    ax.text(2.48, len(labels)-0.3, "Ann. Return", va='top', ha='left',
            color=TEXT_SEC, fontsize=8, style='italic')

    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# CHART 2  ·  GNN Permutation Test — Annotated Step Chart
# ────────────────────────────────────────────────────────────────────────────
def chart_permutation():
    models   = ["Classical PEAD\n(No Graph)",
                "Random GAT\n(Topology Only, n=10)",
                "Trained GAT\n(Topology + Weights)"]
    sharpes  = [1.811, 2.249, 2.259]
    dot_cols = [INDIGO, VIOLET, EMERALD]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    apply_dark_theme(fig, ax)

    x = np.array([0, 1, 2])

    # ── Shaded step regions ──────────────────────────────────────────────
    # Region 1: topological gain (bar from 0 to 1)
    ax.fill_betweenx([1.811, 2.249], -0.15, 0.5, color=TEAL, alpha=0.07, zorder=0)
    # Region 2: weight gain — near invisible (bar from 1 to 2)
    ax.fill_betweenx([2.249, 2.259], 0.5, 2.15, color=VIOLET, alpha=0.05, zorder=0)

    # ── Connecting horizontal dashed lines between points ─────────────────
    ax.hlines(y=1.811, xmin=-0.15, xmax=0.5, color=INDIGO, lw=1, ls='--', alpha=0.5)
    ax.hlines(y=2.249, xmin=0.5, xmax=1.5, color=VIOLET, lw=1, ls='--', alpha=0.5)
    ax.hlines(y=2.259, xmin=1.5, xmax=2.15, color=EMERALD, lw=1, ls='--', alpha=0.5)

    # ── Vertical connecting lines (step connectors) ───────────────────────
    ax.vlines(x=0.5, ymin=1.811, ymax=2.249, color=TEAL, lw=1.2, ls=':', alpha=0.7)
    ax.vlines(x=1.5, ymin=2.249, ymax=2.259, color=VIOLET, lw=1.2, ls=':', alpha=0.5)

    # ── Dots ──────────────────────────────────────────────────────────────
    ax.scatter(x, sharpes, color=dot_cols, s=200, zorder=5, linewidths=0)

    # ── Value labels ──────────────────────────────────────────────────────
    for xi, yi, col in zip(x, sharpes, dot_cols):
        ax.text(xi, yi + 0.015, f"{yi:.3f}", ha='center', va='bottom',
                color=col, fontsize=11, fontweight='bold')

    # ── Delta annotations ─────────────────────────────────────────────────
    # Big delta (topological shift)
    ax.annotate('', xy=(0.5, 2.249), xytext=(0.5, 1.811),
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.5))
    ax.text(0.57, 2.02, "+0.438\nTopological\nGain", color=TEAL,
            fontsize=8.5, fontweight='bold', va='center')

    # Small delta (trained weights)
    ax.annotate('', xy=(1.5, 2.259), xytext=(1.5, 2.249),
                arrowprops=dict(arrowstyle='->', color=VIOLET, lw=1.2))
    ax.text(1.57, 2.253, "+0.010\np = 0.30, n.s.", color=VIOLET,
            fontsize=8, va='center')

    # ── Key insight box ───────────────────────────────────────────────────
    insight = "Alpha is topology-driven, not weight-driven"
    ax.text(1.0, 1.83, insight, ha='center', va='center',
            color=TEXT_PRI, fontsize=9, fontweight='bold',
            bbox=dict(facecolor=SURFACE, edgecolor=BORDER,
                      boxstyle='round,pad=0.5', linewidth=1))

    ax.set_xticks(x)
    ax.set_xticklabels(models, color=TEXT_PRI, fontsize=9.5)
    ax.set_xlim(-0.4, 2.4)
    ax.set_ylim(1.65, 2.43)
    ax.set_ylabel("Annualized Sharpe Ratio (OOS)", color=TEXT_SEC, fontsize=9.5)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
    ax.xaxis.grid(False)
    ax.yaxis.grid(True)

    set_title(ax, "GNN Permutation Test · Topology vs. Learned Weights",
              "Ablation configuration (2021–2026) — Does training the GAT add predictive value beyond graph structure?")

    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# CHART 3  ·  Friction Sensitivity — Area + Line
# ────────────────────────────────────────────────────────────────────────────
def chart_friction():
    frictions = [0, 4, 10, 20, 30, 50]
    sharpes   = [2.410, 2.326, 2.180, 1.850, 1.480, 0.950]

    fig, ax = plt.subplots(figsize=(9, 5))
    apply_dark_theme(fig, ax)

    # Area fill below the curve
    ax.fill_between(frictions, sharpes, 0.5, color=EMERALD, alpha=0.07, zorder=1)

    # Main line
    ax.plot(frictions, sharpes, color=EMERALD, lw=2.5, zorder=3, solid_capstyle='round')

    # Dots on each data point
    ax.scatter(frictions, sharpes, color=EMERALD, s=70, zorder=4, linewidths=0)

    # Value labels slightly above each dot
    for x, y in zip(frictions, sharpes):
        ax.text(x, y + 0.05, f"{y:.2f}", ha='center', va='bottom',
                color=TEXT_PRI, fontsize=9, fontweight='bold')

    # Institutional spread zone
    ax.axvspan(2, 5, color=TEAL, alpha=0.12, zorder=0, label='Institutional Spread (2–5 bps)')
    ax.text(3.5, 0.78, "Typical\nSpread", ha='center', va='bottom',
            color=TEAL, fontsize=7.5, style='italic')

    # Baseline marker (4 bps)
    ax.axvline(x=4, color=TEAL, lw=1, ls='--', alpha=0.6, zorder=2)
    ax.annotate("Baseline (4 bps)\nSharpe = 2.33",
                xy=(4, 2.326),
                xytext=(14, 2.36),
                arrowprops=dict(arrowstyle='->', color=TEXT_SEC, lw=1.0),
                color=TEXT_SEC, fontsize=8.5, fontweight='bold')

    # "Still viable" annotation at the right end
    ax.text(50, 0.95 + 0.08, "Still +ve\nat 50 bps", ha='center', va='bottom',
            color=SLATE_LT, fontsize=7.5, style='italic')

    ax.set_xlim(-2, 54)
    ax.set_ylim(0.5, 2.65)
    ax.set_xlabel("Round-Trip Transaction Cost (bps per trade)", color=TEXT_SEC, fontsize=9.5)
    ax.set_ylabel("Annualized Sharpe Ratio (OOS)", color=TEXT_SEC, fontsize=9.5)
    ax.xaxis.set_major_locator(mticker.FixedLocator(frictions))
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)

    set_title(ax, "Friction Sensitivity & Cost Stress Test",
              "GAT Multiplex (Sector Filtered) · OOS 2021–2026 — Sharpe ratio under increasing transaction costs")

    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir  = os.path.abspath(os.path.join(current_dir, "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)

    print("Generating premium dark-mode performance chart...")
    fig1 = chart_performance()
    fig1.savefig(os.path.join(assets_dir, "gat_performance_comparison.png"),
                 dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close(fig1)

    print("Generating premium dark-mode permutation test chart...")
    fig2 = chart_permutation()
    fig2.savefig(os.path.join(assets_dir, "gnn_permutation_test.png"),
                 dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close(fig2)

    print("Generating premium dark-mode friction sensitivity chart...")
    fig3 = chart_friction()
    fig3.savefig(os.path.join(assets_dir, "friction_sensitivity.png"),
                 dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close(fig3)

    print("SUCCESS: All premium dark-mode charts saved to assets/")

if __name__ == "__main__":
    main()
