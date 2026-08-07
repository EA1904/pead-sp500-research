import os
import sys
import pandas as pd
import numpy as np
import yaml

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from metrics import calculate_metrics
from portfolio_engine import run_custom_portfolio_backtest
from validation.randomness import analyze_randomness

try:
    from model import PEADSurpriseStrategy
except ImportError:
    PEADSurpriseStrategy = None


def run_backtest():
    if PEADSurpriseStrategy is None:
        print("=" * 70)
        print("INFO: PEADSurpriseStrategy (model.py) is withheld for proprietary/academic publication reasons.")
        print("The rest of the backtesting, Fama-French metrics, and statistical DSR engines are shared for transparency.")
        print("=" * 70)
        sys.exit(0)

    print("=" * 70)
    print("   ExploraQuant - PST_012 (PEAD Strategy Backtester - S&P 500 Complet)")
    print("=" * 70)

    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    print("Chargement des cours des actions S&P 500 (391 Mo)... Cela peut prendre quelques secondes...")
    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])

    strategy = PEADSurpriseStrategy()

    with open(os.path.join(local_dir, "2_model", "config.yaml"), "r") as f:
        base_params = yaml.safe_load(f).get("parameters", {})

    variants = {
        "1) Baseline (SUE 1.5, Vol 1.5, SL 5%)": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "2) SUE Aggressif (SUE 1.0)": {
            "sue_threshold": 1.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "3) SUE Conservateur (SUE 2.0)": {
            "sue_threshold": 2.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05
        },
        "4) Sans Filtre de Volume": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 0.0, "holding_period": 20, "stop_loss": 0.05
        },
        "5) Sans Stop Loss": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 1.0
        },
        "6) Holding Court (10 Jours)": {
            "sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 10, "stop_loss": 0.05
        },
        "BH) Buy & Hold S&P 500": {"is_bh": True}
    }

    cutoff = "2020-12-31"
    results_is, results_oos = [], []

    for name, vsettings in variants.items():
        print(f"\n>> Évaluation de la variante : {name}...")

        if vsettings.get("is_bh", False):
            # Pour Buy & Hold, signal=1.0 partout
            df_signals = pd.Series(1.0, index=df_data.index)
        else:
            params = base_params.copy()
            params.update(vsettings)
            df_signals = strategy.predict(df_data, params=params)

        for period in ["IS", "OOS"]:
            if period == "IS":
                mask = df_data["Date"] <= cutoff
            else:
                mask = df_data["Date"] > cutoff

            df_sub = df_data[mask].copy()
            sig_sub = df_signals.loc[df_sub.index].copy()

            if df_sub.empty:
                continue

            res = run_custom_portfolio_backtest(df_sub, sig_sub)
            m = res["metrics"]

            p_val = 1.0
            rets = res["equity_curve"].pct_change().dropna()
            if len(rets) > 5:
                p_val = analyze_randomness(rets).get("runs_test_p_value", 1.0)

            row = {
                "Variante": name,
                "Total Return": m.get("total_return", 0.0),
                "Ann. Return": m.get("annualized_return", 0.0),
                "Sharpe": m.get("sharpe_ratio", 0.0),
                "Sortino": m.get("sortino_ratio", 0.0),
                "Max DD": m.get("max_drawdown", 0.0),
                "Calmar": m.get("calmar_ratio", 0.0),
                "Trades": m.get("total_trades", 0),
                "PF": m.get("profit_factor", 0.0),
                "Win Rate": m.get("win_rate", 0.0),
                "p-value": p_val,
                "Sig.": "Oui" if p_val < 0.05 else "Non"
            }

            if period == "IS":
                results_is.append(row)
            else:
                results_oos.append(row)

    # Affichage
    for label, data in [("IN-SAMPLE (2015-2020)", results_is), ("OUT-OF-SAMPLE (2021-2026)", results_oos)]:
        print(f"\n{'='*95}\n  {label}\n{'='*95}")
        df_p = pd.DataFrame(data)
        for c in ["Total Return", "Ann. Return", "Max DD", "Win Rate"]:
            df_p[c] = df_p[c].apply(lambda x: f"{x:.2%}")
        for c in ["Sharpe", "Sortino", "PF", "Calmar"]:
            df_p[c] = df_p[c].apply(lambda x: f"{x:.3f}")
        print(df_p.to_string(index=False))

    # Enregistrer results_comparison.md
    md_path = os.path.join(local_dir, "3_backtest", "results_comparison.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Rapport de Backtest Comparatif : PST_012 PEAD Strategy (S&P 500 Complet)\n\n")
        f.write("Ce rapport compare les performances de la stratégie Post-Earnings-Announcement Drift (PST_012) ")
        f.write("sur le portefeuille complet de l'univers S&P 500 (actions disponibles).\n\n")

        for label, data in [("In-Sample (2015-2020)", results_is), ("Out-of-Sample (2021-2026)", results_oos)]:
            f.write(f"## {label}\n\n")
            f.write("| Variante | Rendement Cumulé | Rendement Ann. | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Significatif ? |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
            for r in data:
                f.write(f"| {r['Variante']} | {r['Total Return']:.2%} | {r['Ann. Return']:.2%} | {r['Sharpe']:.3f} | {r['Max DD']:.2%} | {r['Trades']} | {r['PF']:.3f} | {r['Win Rate']:.2%} | {r['p-value']:.4f} | {r['Sig.']} |\n")
            f.write("\n")

    print(f"\nRapport Markdown enregistré dans : {md_path}")
    print("Backtest terminé avec succès !")


if __name__ == "__main__":
    run_backtest()
