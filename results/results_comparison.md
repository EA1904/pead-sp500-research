# Rapport de Backtest Comparatif : PEAD-Surprise Strategy (S&P 500 Complet)

Ce rapport compare les performances de la stratégie Post-Earnings-Announcement Drift (PEAD-Surprise) sur le portefeuille complet de l'univers S&P 500 (actions disponibles).

## In-Sample (2015-2020)

| Variante | Rendement Cumulé | Rendement Ann. | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Significatif ? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1) Baseline (SUE 1.5, Vol 1.5, SL 5%) | 1278.63% | 69.14% | 3.149 | -17.08% | 1919 | 1.773 | 54.19% | 0.9810 | Non |
| 2) SUE Aggressif (SUE 1.0) | 1112.63% | 64.85% | 3.303 | -12.47% | 2789 | 1.697 | 53.14% | 0.8923 | Non |
| 3) SUE Conservateur (SUE 2.0) | 1872.51% | 81.73% | 3.353 | -14.88% | 1326 | 1.792 | 54.07% | 0.4500 | Non |
| 4) Sans Filtre de Volume | 1043.90% | 62.93% | 3.108 | -17.31% | 2690 | 1.924 | 55.58% | 0.7677 | Non |
| 5) Sans Stop Loss | 771.08% | 54.28% | 2.800 | -14.79% | 1919 | 1.999 | 60.45% | 0.9636 | Non |
| 6) Holding Court (10 Jours) | 4613.46% | 116.37% | 3.325 | -15.03% | 1919 | 1.647 | 54.66% | 0.1162 | Non |
| BH) Buy & Hold S&P 500 | 78.12% | 12.26% | 0.908 | -20.35% | 581 | 12.683 | 78.83% | 0.1397 | Non |

## Out-of-Sample (2021-2026)

| Variante | Rendement Cumulé | Rendement Ann. | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Significatif ? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1) Baseline (SUE 1.5, Vol 1.5, SL 5%) | 1379.41% | 66.17% | 2.531 | -23.84% | 2284 | 1.878 | 53.33% | 0.2175 | Non |
| 2) SUE Aggressif (SUE 1.0) | 1006.52% | 57.31% | 2.508 | -17.54% | 3353 | 1.756 | 51.57% | 0.0567 | Non |
| 3) SUE Conservateur (SUE 2.0) | 2406.49% | 83.53% | 2.715 | -23.71% | 1581 | 1.917 | 53.32% | 0.0230 | Oui |
| 4) Sans Filtre de Volume | 1078.85% | 59.20% | 2.452 | -20.16% | 3418 | 1.979 | 53.31% | 0.4231 | Non |
| 5) Sans Stop Loss | 831.61% | 52.29% | 2.171 | -19.84% | 2282 | 2.087 | 60.39% | 0.9611 | Non |
| 6) Holding Court (10 Jours) | 9356.99% | 135.72% | 2.930 | -22.86% | 2310 | 2.088 | 58.44% | 0.0189 | Oui |
| BH) Buy & Hold S&P 500 | 104.30% | 14.41% | 0.855 | -21.74% | 598 | 10.698 | 70.90% | 0.2328 | Non |

