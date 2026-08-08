"""
📈 Générateur de Graphiques de Performance Professionnels — PEAD S&P 500
================================================================================
Ce script exécute le backtest complet localement (nécessite model.py et les données raw)
et génère un graphique double (Equity Curve & Drawdowns) de niveau institutionnel.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

# Gestion des imports locaux et du modèle local
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
        print("ERROR: PEADSurpriseStrategy (model.py) non trouvé.")
        print("Veuillez exécuter ce script depuis votre ordinateur de travail où le code original est disponible.")
        sys.exit(1)

    print("Initialisation du backtest et chargement des données...")
    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    if not os.path.exists(price_data_path):
        print(f"ERROR: Données de prix introuvables à : {price_data_path}")
        sys.exit(1)

    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])

    # Récupérer les paramètres par défaut de la variante 6
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(ORIGINAL_MODEL_DIR, "config.yaml")
    
    base_params = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_params = yaml.safe_load(f).get("parameters", {})

    # Paramètres de la Variante 6 (Holding 10J, SUE 1.5, Vol 1.5, SL 5%)
    params = base_params.copy()
    params.update({
        "sue_threshold": 1.5,
        "vol_expansion_threshold": 1.5,
        "holding_period": 10,
        "stop_loss": 0.05
    })

    print("Génération des signaux de la stratégie...")
    strategy = PEADSurpriseStrategy()
    df_signals = strategy.predict(df_data, params=params)

    # Filtrer pour la période OOS (Out-of-Sample) 2021-2026 pour démonstration
    cutoff = "2020-12-31"
    
    # 1. Backtest PEAD (OOS)
    df_data_oos = df_data[df_data["Date"] > cutoff].copy()
    df_signals_oos = df_signals.loc[df_data_oos.index].copy()
    
    print("Exécution du backtest OOS (PEAD Variante 6)...")
    res_pead = run_custom_portfolio_backtest(df_data_oos, df_signals_oos, initial_capital=100000.0, cost_bps=4.0)
    
    # 2. Backtest Benchmark Buy & Hold
    print("Exécution du backtest OOS (Buy & Hold S&P 500)...")
    df_signals_bh = pd.Series(1.0, index=df_data_oos.index)
    res_bh = run_custom_portfolio_backtest(df_data_oos, df_signals_bh, initial_capital=100000.0, cost_bps=0.0)

    # Calcul des courbes d'equity normalisées à 100
    pead_equity = (res_pead["equity_curve"] / 100000.0) * 100.0
    bh_equity = (res_bh["equity_curve"] / 100000.0) * 100.0

    # Calcul des Drawdowns
    pead_dd = (pead_equity - pead_equity.cummax()) / pead_equity.cummax() * 100.0
    bh_dd = (bh_equity - bh_equity.cummax()) / bh_equity.cummax() * 100.0

    # Création du graphique
    print("Tracé des courbes de performance...")
    sns.set_theme(style="darkgrid")
    
    # Palette de couleurs professionnelles
    color_pead = "#0F9D58"  # Vert émeraude quant
    color_bh = "#4285F4"    # Bleu benchmark
    color_dd = "#DB4437"    # Rouge drawdown

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1.2]})

    # 1. Courbe d'Equity (Échelle logarithmique pour la lisibilité)
    ax1.plot(pead_equity.index, pead_equity.values, label=f"PEAD-Surprise (OOS Sharpe: {res_pead['metrics']['sharpe_ratio']:.3f})", color=color_pead, linewidth=2.5)
    ax1.plot(bh_equity.index, bh_equity.values, label=f"S&P 500 Buy & Hold (OOS Sharpe: {res_bh['metrics']['sharpe_ratio']:.3f})", color=color_bh, linewidth=1.5, linestyle="--")
    
    ax1.set_yscale('log')
    ax1.set_title("Performance Out-of-Sample (OOS) — 2021-2026\nPEAD-Surprise Strategy vs S&P 500 Index (Frais net: 4.0 bps / trade)", fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel("Capital Indexé (Base 100 - Échelle Log)", fontsize=12)
    ax1.legend(loc="upper left", fontsize=11, frameon=True)
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Formater les ticks de l'axe Y en valeurs réelles (ex: 100, 1000, 10000)
    import matplotlib.ticker as ticker
    ax1.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    # 2. Graphique de Drawdown
    ax2.fill_between(pead_dd.index, pead_dd.values, 0, label="PEAD Drawdown", color=color_pead, alpha=0.4)
    ax2.fill_between(bh_dd.index, bh_dd.values, 0, label="S&P 500 Drawdown", color=color_bh, alpha=0.2)
    
    ax2.set_ylabel("Drawdown (%)", fontsize=12)
    ax2.set_ylim(-60, 2)
    ax2.legend(loc="lower left", fontsize=10)
    ax2.grid(True, ls="--", alpha=0.5)

    # Ajustement final
    plt.tight_layout()
    
    # Enregistrer dans le dossier assets du repo
    assets_dir = os.path.join(local_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    out_img_path = os.path.join(assets_dir, "pead_performance.png")
    
    plt.savefig(out_img_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"SUCCESS: Graphique de performance enregistré avec succès à : {out_img_path}")


if __name__ == "__main__":
    generate_plots()
