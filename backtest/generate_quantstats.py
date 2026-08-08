import os
import sys
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import quantstats as qs

# Configuration pour charger le modèle local
ORIGINAL_MODEL_DIR = r"C:\Users\DELL\Desktop\PHD\Expoloration\Lab\PST_012_pead_surprise_strategy\500SP\2_model"
sys.path.append(ORIGINAL_MODEL_DIR)
sys.path.append(os.path.dirname(__file__))

try:
    from model import PEADSurpriseStrategy
except ImportError:
    PEADSurpriseStrategy = None

from portfolio_engine import run_custom_portfolio_backtest

def main():
    if PEADSurpriseStrategy is None:
        print("ERROR: PEADSurpriseStrategy (model.py) non trouvé.")
        sys.exit(1)

    print("Chargement des données...")
    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])
    
    # Exclure 2020 pour la cohérence IS/OOS
    df_data = df_data[df_data["Date"].dt.year != 2020].reset_index(drop=True)

    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(ORIGINAL_MODEL_DIR, "config.yaml")
    
    base_params = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_params = yaml.safe_load(f).get("parameters", {})

    # Paramètres de la Variante 6
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

    # Filtrer pour la période OOS (2021-2026)
    cutoff = "2020-12-31"
    df_data_oos = df_data[df_data["Date"] > cutoff].copy()
    df_signals_oos = df_signals.loc[df_data_oos.index].copy()

    print("Exécution des backtests...")
    res_pead = run_custom_portfolio_backtest(df_data_oos, df_signals_oos, initial_capital=100000.0, cost_bps=4.0)
    res_bh = run_custom_portfolio_backtest(df_data_oos, pd.Series(1.0, index=df_data_oos.index), initial_capital=100000.0, cost_bps=0.0)

    # Extraction des rendements journaliers
    pead_equity = res_pead["equity_curve"]
    bh_equity = res_bh["equity_curve"]

    # S'assurer que l'index est bien au format DatetimeIndex
    pead_equity.index = pd.to_datetime(pead_equity.index)
    bh_equity.index = pd.to_datetime(bh_equity.index)

    returns = pead_equity.pct_change().dropna()
    benchmark = bh_equity.pct_change().dropna()

    # Alignement temporel des index
    returns, benchmark = returns.align(benchmark, join='inner')

    print("Génération des rapports graphiques via QuantStats...")
    assets_dir = os.path.join(local_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Heatmap mensuelle
    heatmap_path = os.path.join(assets_dir, "quantstats_monthly_heatmap.png")
    print(f"Création de la Heatmap mensuelle -> {heatmap_path}")
    qs.plots.monthly_heatmap(returns, savefig=heatmap_path, show=False)
    plt.close()

    # 2. Cumulative Returns vs Benchmark
    returns_path = os.path.join(assets_dir, "quantstats_cumulative_returns.png")
    print(f"Création de la courbe comparative -> {returns_path}")
    # Modifier la palette de couleur pour correspondre à notre style (Vert/Bleu)
    # QuantStats utilise matplotlib sous le capot, on peut configurer le plot
    qs.plots.returns(returns, benchmark, savefig=returns_path, show=False)
    plt.close()

    # 3. Drawdowns
    drawdown_path = os.path.join(assets_dir, "quantstats_drawdown.png")
    print(f"Création de la courbe des Drawdowns -> {drawdown_path}")
    qs.plots.drawdown(returns, savefig=drawdown_path, show=False)
    plt.close()

    print("SUCCESS: Tous les rapports visuels de performance ont été générés dans le dossier assets/ !")

if __name__ == "__main__":
    main()
