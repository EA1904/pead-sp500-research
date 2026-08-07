# Rapport de Backtest Comparatif : PST_012 PEAD Strategy (S&P 500 Complet)

Ce rapport compare les performances de la stratégie Post-Earnings-Announcement Drift (PST_012) sur le portefeuille complet de l'univers S&P 500 (actions disponibles).

## In-Sample (2015-2020)

| Variante | Rendement Cumulé | Rendement Ann. | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Autocorr. ? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1) Baseline (SUE 1.5, Vol 1.5, SL 5%) | 1273.91% | 54.81% | 2.029 | -48.16% | 2403 | 1.728 | 52.14% | 0.9134 | Non |
| 2) SUE Aggressif (SUE 1.0) | 1198.05% | 53.35% | 1.778 | -42.97% | 3416 | 1.674 | 51.67% | 0.5846 | Non |
| 3) SUE Conservateur (SUE 2.0) | 2378.28% | 70.81% | 2.554 | -28.80% | 1720 | 1.753 | 51.69% | 0.2180 | Non |
| 4) Sans Filtre de Volume | 1385.07% | 56.83% | 2.020 | -46.73% | 3562 | 1.868 | 53.31% | 0.8332 | Non |
| 5) Sans Stop Loss | 1093.26% | 51.21% | 1.985 | -39.43% | 2403 | 1.922 | 60.59% | 0.5764 | Non |
| **6) Holding Court (10 Jours)** | **5067.37%** | **93.08%** | **2.504** | **-45.97%** | **2403** | **1.648** | **53.64%** | **0.0788** | **Non** |
| 📌 Benchmark : Achat Post-Earnings (sans filtre) | 193.70% | 19.68% | 0.909 | -33.23% | 12796 | 1.256 | 50.39% | — | — |
| BH) Buy & Hold S&P 500 | 115.82% | 13.69% | 0.732 | -39.92% | 586 | 16.081 | 76.28% | 0.0252 | Oui |

## Out-of-Sample (2021-2026)

| Variante | Rendement Cumulé | Rendement Ann. | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Autocorr. ? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1) Baseline (SUE 1.5, Vol 1.5, SL 5%) | 1214.93% | 62.51% | 2.411 | -23.84% | 2017 | 1.729 | 51.81% | 0.1216 | Non |
| 2) SUE Aggressif (SUE 1.0) | 928.85% | 55.17% | 2.426 | -17.54% | 3048 | 1.627 | 50.03% | 0.0509 | Non |
| 3) SUE Conservateur (SUE 2.0) | 2067.95% | 78.58% | 2.573 | -23.71% | 1334 | 1.768 | 51.80% | 0.0186 | Oui |
| 4) Sans Filtre de Volume | 943.06% | 55.57% | 2.325 | -20.16% | 3043 | 1.789 | 51.99% | 0.2893 | Non |
| 5) Sans Stop Loss | 752.27% | 49.76% | 2.083 | -19.84% | 2019 | 1.910 | 59.53% | 0.7203 | Non |
| **6) Holding Court (10 Jours)** | **9207.74%** | **135.01%** | **2.911** | **-22.86%** | **2013** | **1.789** | **56.04%** | **0.0175** | **Oui** |
| 📌 Benchmark : Achat Post-Earnings (sans filtre) | 112.68% | 15.28% | 0.745 | -24.56% | 11965 | 1.284 | 50.35% | — | — |
| BH) Buy & Hold S&P 500 | 104.30% | 14.41% | 0.855 | -21.74% | 598 | 10.698 | 70.90% | 0.2328 | Non |
