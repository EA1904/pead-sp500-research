import os
import sys
import pandas as pd
import numpy as np
import scipy.stats as stats
import yaml

sys.path.append(os.path.dirname(__file__))

# Local model folder fallback
ORIGINAL_MODEL_DIR = r"C:\Users\DELL\Desktop\PHD\Expoloration\Lab\PST_012_pead_surprise_strategy\500SP\2_model"
sys.path.append(ORIGINAL_MODEL_DIR)

from metrics import calculate_metrics
from portfolio_engine import run_custom_portfolio_backtest

try:
    from model import PEADSurpriseStrategy
except ImportError:
    PEADSurpriseStrategy = None


def expected_max_sharpe(sharpe_variance, n_trials):
    """
    Calcule le Sharpe maximum attendu sous l'hypothèse nulle (stratégies aléatoires).
    Méthode d'approximation de Bailey et Lopez de Prado (2012).
    """
    if n_trials <= 1:
        return 0.0

    euler_gamma = 0.5772156649
    z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    expected_standard_max = (1.0 - euler_gamma) * z1 + euler_gamma * z2
    return np.sqrt(sharpe_variance) * expected_standard_max


def calculate_dsr(best_sharpe, all_sharpes, returns_series, annualization_factor=252):
    """
    Calcule le Deflated Sharpe Ratio (DSR) d'après les formules de Bailey et Lopez de Prado.
    """
    T = len(returns_series)
    if T < 5:
        return 0.0

    n_trials = len(all_sharpes)
    sharpe_variance = np.var(all_sharpes, ddof=1) if n_trials > 1 else 0.0

    sr_0 = expected_max_sharpe(sharpe_variance, n_trials)

    skew = stats.skew(returns_series)
    kurt = stats.kurtosis(returns_series, fisher=True) + 3.0

    sr_ann = best_sharpe
    sr_daily = sr_ann / np.sqrt(annualization_factor)
    sr_0_daily = sr_0 / np.sqrt(annualization_factor)

    var_sr_daily = (1.0 - skew * sr_daily + ((kurt - 1.0) / 4.0) * (sr_daily ** 2)) / (T - 1.0)

    z_stat = (sr_daily - sr_0_daily) / np.sqrt(var_sr_daily)
    dsr = stats.norm.cdf(z_stat)

    return {
        "dsr": float(dsr),
        "expected_max_sharpe": float(sr_0),
        "sharpe_variance": float(sharpe_variance),
        "skewness": float(skew),
        "kurtosis": float(kurt),
        "z_statistic": float(z_stat),
        "n_trials": n_trials,
        "observations": T
    }


def main():
    if PEADSurpriseStrategy is None:
        print("=" * 60)
        print("INFO: PEADSurpriseStrategy (model.py) is withheld for proprietary/academic publication reasons.")
        print("The rest of the backtesting, Fama-French metrics, and statistical DSR engines are shared for transparency.")
        print("=" * 60)
        sys.exit(0)

    print("=" * 60)
    print("       ExploraQuant - DSR Calculator (PEAD-Surprise - S&P 500 Complet)")
    print("=" * 60)

    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    price_data_path = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"
    df_data = pd.read_parquet(price_data_path)
    df_data['Date'] = pd.to_datetime(df_data['Date'])
    # Éliminer l'année 2020 (choc COVID atypique)
    df_data = df_data[df_data["Date"].dt.year != 2020].reset_index(drop=True)

    strategy = PEADSurpriseStrategy()

    with open(os.path.join(ORIGINAL_MODEL_DIR, "config.yaml"), "r") as f:
        model_config = yaml.safe_load(f)
    base_params = model_config.get("parameters", {})

    variants = [
        {"sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05},
        {"sue_threshold": 1.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05},
        {"sue_threshold": 2.0, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 0.05},
        {"sue_threshold": 1.5, "vol_expansion_threshold": 0.0, "holding_period": 20, "stop_loss": 0.05},
        {"sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 20, "stop_loss": 1.0},
        {"sue_threshold": 1.5, "vol_expansion_threshold": 1.5, "holding_period": 10, "stop_loss": 0.05}
    ]

    sharpes = []
    best_returns = None
    best_sharpe = -999.0

    print("Exécution des simulations pour chaque variante...")
    for idx, var_params in enumerate(variants):
        params = base_params.copy()
        params.update(var_params)

        df_sig = strategy.predict(df_data, params=params)
        res = run_custom_portfolio_backtest(df_data, df_sig)

        sh = res["metrics"]["sharpe_ratio"]
        sharpes.append(sh)
        print(f"  Variante {idx+1} Sharpe : {sh:.4f}")

        if sh > best_sharpe:
            best_sharpe = sh
            best_returns = res["equity_curve"].pct_change().dropna()

    dsr_metrics = calculate_dsr(best_sharpe, sharpes, best_returns)

    print("\n" + "-" * 50)
    print("RÉSULTATS DU DEFLATED SHARPE RATIO (DSR) - PEAD-Surprise (S&P 500 Complet) :")
    print(f"  Nombre d'essais (N)         : {dsr_metrics['n_trials']}")
    print(f"  Sharpe Ann. du Meilleur     : {best_sharpe:.4f}")
    print(f"  Variance des Sharpes        : {dsr_metrics['sharpe_variance']:.6f}")
    print(f"  Sharpe Max Attendu (SR_0)   : {dsr_metrics['expected_max_sharpe']:.4f}")
    print(f"  Skewness des rendements     : {dsr_metrics['skewness']:.4f}")
    print(f"  Kurtosis des rendements     : {dsr_metrics['kurtosis']:.4f}")
    print(f"  Statistique Z de Prado      : {dsr_metrics['z_statistic']:.4f}")
    print(f"  Deflated Sharpe Ratio (DSR) : {dsr_metrics['dsr']:.2%}")
    print("-" * 50)
 
    if dsr_metrics['dsr'] >= 0.95:
        print("SIGNIFICATIVITÉ : Le modèle franchit le seuil requis (DSR >= 95%).")
    else:
        print("WARNING : Risque élevé de surapprentissage (DSR < 95%).")
 
    report_path = os.path.join(local_dir, "results", "dsr_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Rapport de Deflated Sharpe Ratio (DSR) : PEAD-Surprise (S&P 500 Complet)\n\n")
        f.write("Ce rapport applique la méthodologie de Marcos López de Prado pour corriger le biais de sélection multiple ")
        f.write("lié au test des 6 variantes de la stratégie PEAD sur l'univers S&P 500 Complet.\n\n")
        f.write("## Statistiques\n\n")
        f.write(f"- **Nombre d'essais (N)** : {dsr_metrics['n_trials']}\n")
        f.write(f"- **Meilleur Sharpe Ratio Ann.** : {best_sharpe:.4f}\n")
        f.write(f"- **Variance des Sharpe Ratios** : {dsr_metrics['sharpe_variance']:.6f}\n")
        f.write(f"- **Sharpe Attendu par simple chance (SR_0)** : {dsr_metrics['expected_max_sharpe']:.4f}\n")
        f.write(f"- **Asymétrie (Skewness)** : {dsr_metrics['skewness']:.4f}\n")
        f.write(f"- **Cacuminosité (Kurtosis)** : {dsr_metrics['kurtosis']:.4f}\n")
        f.write(f"- **DSR (Deflated Sharpe Ratio)** : **{dsr_metrics['dsr']:.2%}**\n\n")
        f.write("## Conclusion Académique\n\n")
        if dsr_metrics['dsr'] >= 0.95:
            f.write("Le DSR est supérieur au seuil critique de 95%, ce qui valide de manière statistique robuste ")
            f.write("que la surperformance de la meilleure variante PEAD n'est pas le produit du hasard.\n")
        else:
            f.write("Le DSR est inférieur au seuil critique de 95%, suggérant un risque de surapprentissage.\n")

    print(f"\nRapport DSR enregistré dans : {report_path}")


if __name__ == "__main__":
    main()
