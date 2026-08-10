"""
Premium Chart Generator — PEAD + GAT Multiplex
Style: Blue-Gray Muted (C) — minimalist, light background
================================================================================
Palette:
  BG       #EEF2F7  — blue-tinted light gray background
  SURFACE  #F8FAFC  — card surface
  BORDER   #CBD5E1  — subtle borders / grid
  TEXT_PRI #1E293B  — primary text (dark slate)
  TEXT_SEC #64748B  — secondary text / labels
  BARS     #B0BEC5 → #90A4AE → #78909C → #5C8DB8 → #3A7BD5 → #1565C0
  ACCENT   #1565C0  — strong blue accent (top performer / annotations)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#EEF2F7"
SURFACE   = "#F8FAFC"
BORDER    = "#CBD5E1"
TEXT_PRI  = "#1E293B"
TEXT_SEC  = "#64748B"
ACCENT    = "#1565C0"
BAR_TOP   = "#1565C0"
BAR_MID2  = "#3A7BD5"
BAR_MID1  = "#5C8DB8"
BAR_BASE  = "#78909C"
BAR_BENCH = "#90A4AE"
BAR_BENCH2= "#B0BEC5"


def apply_theme(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(SURFACE)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
        sp.set_linewidth(0.8)
    ax.tick_params(colors=TEXT_SEC, labelsize=9.5)
    ax.xaxis.label.set_color(TEXT_SEC)
    ax.yaxis.label.set_color(TEXT_SEC)


def set_title(ax, title, subtitle=None):
    pad = 34 if subtitle else 12
    ax.set_title(title, loc="left", color=TEXT_PRI, fontsize=13,
                 fontweight="bold", pad=pad)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1.09), xycoords="axes fraction",
                    ha="left", va="bottom", color=TEXT_SEC,
                    fontsize=8.2, annotation_clip=False)


# ────────────────────────────────────────────────────────────────────────────
# CHART 1 · Performance Comparison
# ────────────────────────────────────────────────────────────────────────────
def chart_performance():
    labels  = ["S&P 500 Buy & Hold",
               "Naive Post-Earnings",
               "Classical PEAD (Baseline)",
               "GAT Multiplex · Long-Only",
               "GAT Multiplex · Long-Short",
               "GAT Multiplex · Sector Filtered  ★"]
    sharpes = [0.855, 0.745, 2.131, 2.180, 2.240, 2.326]
    returns = [14.41, 15.28, 77.73, 79.15, 80.50, 81.88]
    bar_col = [BAR_BENCH2, BAR_BENCH, BAR_BASE, BAR_MID1, BAR_MID2, BAR_TOP]

    fig, ax = plt.subplots(figsize=(11, 5.4))
    apply_theme(fig, ax)

    y = np.arange(len(labels))

    # Subtle highlight band for GAT rows
    ax.axhspan(2.42, 5.58, color=ACCENT, alpha=0.05, zorder=0)
    # Separator line between baseline & GAT
    ax.axhline(y=2.48, color=BORDER, lw=1.0, linestyle="--", alpha=0.9)

    ax.grid(axis="x", color=BORDER, linestyle="-", linewidth=0.6)
    ax.yaxis.grid(False)

    for i, (sh, ret, col) in enumerate(zip(sharpes, returns, bar_col)):
        ax.barh(i, sh, height=0.50, color=col, zorder=2)
        # Value label
        lbl_col = "#FFFFFF" if i >= 3 else TEXT_PRI
        ax.text(sh - 0.06, i, f"{sh:.3f}", va="center", ha="right",
                color=lbl_col, fontsize=10.5, fontweight="bold", zorder=4)
        # Ann. Return on right
        ret_col = ACCENT if i == len(labels) - 1 else TEXT_SEC
        ax.text(2.50, i, f"+{ret:.1f}%", va="center", ha="left",
                color=ret_col, fontsize=8.5)

    # Category separators
    ax.text(0.015, 1.62, "Passive Benchmarks", color=BAR_BENCH,
            fontsize=7.5, style="italic", ha="left", va="center")
    ax.text(0.015, 4.82, "GAT Network-Augmented", color=ACCENT,
            fontsize=7.5, style="italic", ha="left", va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, color=TEXT_PRI, fontsize=9.5)
    ax.set_xlim(0, 2.60)
    ax.set_ylim(-0.55, 5.85)
    ax.set_xlabel("Annualized Sharpe Ratio (OOS 2021–2026)",
                  color=TEXT_SEC, fontsize=9.5)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.text(2.50, 5.65, "Ann. Return", va="center", ha="left",
            color=TEXT_SEC, fontsize=8, style="italic")

    set_title(ax, "Out-of-Sample Performance — OOS 2021–2026",
              "S&P 500 Universe (590 stocks)  ·  T+1 Open Execution  ·  4.0 bps friction")
    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# CHART 2 · GNN Permutation Test
# ────────────────────────────────────────────────────────────────────────────
def chart_permutation():
    models  = ["Classical PEAD\n(No Graph)",
               "Random GAT\n(Topology Only, n=10)",
               "Trained GAT\n(Topology + Weights)"]
    sharpes = [1.811, 2.249, 2.259]
    dot_col = [BAR_BASE, BAR_MID2, BAR_TOP]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    apply_theme(fig, ax)

    x = np.array([0, 1, 2])

    # Shaded region for topological gain
    ax.fill_betweenx([1.811, 2.249], -0.25, 0.5,
                     color=ACCENT, alpha=0.06, zorder=0)

    # Dashed horizontal connectors
    ax.hlines(1.811, -0.25, 0.5, color=BAR_BASE, lw=1.2, ls="--", alpha=0.5)
    ax.hlines(2.249, 0.5, 1.5, color=BAR_MID2, lw=1.2, ls="--", alpha=0.5)
    ax.hlines(2.259, 1.5, 2.25, color=BAR_TOP, lw=1.2, ls="--", alpha=0.5)

    # Step connectors
    ax.vlines(0.5, 1.811, 2.249, color=ACCENT, lw=1.5, ls=":", alpha=0.7)
    ax.vlines(1.5, 2.249, 2.259, color=BAR_MID2, lw=1.2, ls=":", alpha=0.5)

    # Dots
    ax.scatter(x, sharpes, color=dot_col, s=180, zorder=5, linewidths=0)

    # Value labels
    for xi, yi, col in zip(x, sharpes, dot_col):
        ax.text(xi, yi + 0.014, f"{yi:.3f}", ha="center", va="bottom",
                color=col, fontsize=11.5, fontweight="bold")

    # Big delta arrow
    ax.annotate("", xy=(0.5, 2.249), xytext=(0.5, 1.811),
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.8))
    ax.text(0.58, 2.02, "+0.438\nTopological\nGain", color=ACCENT,
            fontsize=8.5, fontweight="bold", va="center")

    # Small delta - place below the connector line to avoid overlap with dot and line
    ax.annotate("", xy=(1.5, 2.259), xytext=(1.5, 2.249),
                arrowprops=dict(arrowstyle="->", color=BAR_MID2, lw=1.2))
    ax.text(1.58, 2.21, "+0.010 · p = 0.30 (n.s.)",
            color=TEXT_SEC, fontsize=8, ha="left", va="center")

    # Insight box
    ax.text(1.0, 1.83, "Alpha is topology-driven, not weight-driven",
            ha="center", va="center", color=TEXT_PRI, fontsize=9,
            fontweight="bold",
            bbox=dict(facecolor=SURFACE, edgecolor=BORDER,
                      boxstyle="round,pad=0.5", linewidth=1))

    ax.set_xticks(x)
    ax.set_xticklabels(models, color=TEXT_PRI, fontsize=9.5)
    ax.set_xlim(-0.45, 2.45)
    ax.set_ylim(1.65, 2.43)
    ax.set_ylabel("Annualized Sharpe Ratio (OOS)", color=TEXT_SEC, fontsize=9.5)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
    ax.xaxis.grid(False)
    ax.yaxis.grid(True, color=BORDER, linestyle="-", linewidth=0.6)

    set_title(ax, "GNN Permutation Test · Topology vs. Learned Weights",
              "Ablation study (2021–2026) — Does training the GAT add value beyond graph structure?")
    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# CHART 3 · Friction Sensitivity
# ────────────────────────────────────────────────────────────────────────────
def chart_friction():
    frictions = [0, 4, 10, 20, 30, 50]
    sharpes   = [2.410, 2.326, 2.180, 1.850, 1.480, 0.950]

    fig, ax = plt.subplots(figsize=(9, 5.0))
    apply_theme(fig, ax)

    # Area fill
    ax.fill_between(frictions, sharpes, 0.5,
                    color=ACCENT, alpha=0.07, zorder=1)

    # Main line
    ax.plot(frictions, sharpes, color=ACCENT, lw=2.5,
            zorder=3, solid_capstyle="round")

    # Dots
    ax.scatter(frictions, sharpes, color=ACCENT, s=65, zorder=4)

    # Value labels
    for x, y in zip(frictions, sharpes):
        ax.text(x, y + 0.05, f"{y:.2f}", ha="center", va="bottom",
                color=TEXT_PRI, fontsize=9, fontweight="bold")

    # Institutional spread zone
    ax.axvspan(2, 5, color=BAR_MID1, alpha=0.12, zorder=0)
    ax.text(3.5, 0.65, "Typical\nSpread", ha="center", va="bottom",
            color=BAR_MID1, fontsize=7.5, style="italic")

    # Baseline marker
    ax.axvline(x=4, color=ACCENT, lw=1.0, ls="--", alpha=0.5, zorder=2)
    ax.annotate("Baseline (4 bps) · Sharpe = 2.33",
                xy=(4, 2.326), xytext=(14, 2.38),
                arrowprops=dict(arrowstyle="->", color=TEXT_SEC, lw=1.0),
                color=TEXT_SEC, fontsize=8.5, fontweight="bold")

    # End note - draw below the dot to avoid overlapping value label
    ax.text(50, 0.95 - 0.12, "Sharpe > 0\nat 50 bps", ha="center",
            va="top", color=TEXT_SEC, fontsize=7.5, style="italic")

    ax.set_xlim(-2, 54)
    ax.set_ylim(0.5, 2.65)
    ax.set_xlabel("Round-Trip Transaction Cost (bps per trade)",
                  color=TEXT_SEC, fontsize=9.5)
    ax.set_ylabel("Annualized Sharpe Ratio (OOS)", color=TEXT_SEC, fontsize=9.5)
    ax.xaxis.set_major_locator(mticker.FixedLocator(frictions))
    ax.yaxis.grid(True, color=BORDER, linestyle="-", linewidth=0.6)
    ax.xaxis.grid(False)

    set_title(ax, "Friction Sensitivity & Cost Stress Test",
              "GAT Multiplex (Sector Filtered) · OOS 2021–2026 — Robustness under increasing transaction costs")
    plt.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir  = os.path.abspath(os.path.join(current_dir, "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)

    print("Generating performance comparison chart...")
    fig1 = chart_performance()
    fig1.savefig(os.path.join(assets_dir, "gat_performance_comparison.png"),
                 dpi=300, bbox_inches="tight", facecolor=BG)
    plt.close(fig1)

    print("Generating GNN permutation test chart...")
    fig2 = chart_permutation()
    fig2.savefig(os.path.join(assets_dir, "gnn_permutation_test.png"),
                 dpi=300, bbox_inches="tight", facecolor=BG)
    plt.close(fig2)

    print("Generating friction sensitivity chart...")
    fig3 = chart_friction()
    fig3.savefig(os.path.join(assets_dir, "friction_sensitivity.png"),
                 dpi=300, bbox_inches="tight", facecolor=BG)
    plt.close(fig3)

    print("SUCCESS — all 3 charts saved to assets/")


if __name__ == "__main__":
    main()
