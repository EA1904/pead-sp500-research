# 📊 Comparative Backtest Report: PEAD-Surprise Strategy (Full S&P 500)

This report presents the comparative performance metrics of the Post-Earnings-Announcement Drift (PEAD-Surprise) strategy across different signal variants over the historical S&P 500 constituent universe.

---

## 📈 In-Sample Performance (2015–2020)

All results are net of a standard 4.0 bps execution friction per trade. The COVID-19 structural break (2020) is excluded to maintain parameter calibration homogeneity.

| Variant | Cumulative Return | Ann. Return | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1) Baseline (SUE 1.5, Vol 1.5, SL 5%)** | 1278.63% | 69.14% | 3.149 | -17.08% | 1,919 | 1.773 | 54.19% | 0.9810 | No |
| **2) Aggressive SUE (SUE 1.0)** | 1112.63% | 64.85% | 3.303 | -12.47% | 2,789 | 1.697 | 53.14% | 0.8923 | No |
| **3) Conservative SUE (SUE 2.0)** | 1872.51% | 81.73% | 3.353 | -14.88% | 1,326 | 1.792 | 54.07% | 0.4500 | No |
| **4) Without Volume Filter** | 1043.90% | 62.93% | 3.108 | -17.31% | 2,690 | 1.924 | 55.58% | 0.7677 | No |
| **5) Without Stop Loss** | 771.08% | 54.28% | 2.800 | -14.79% | 1,919 | 1.999 | 60.45% | 0.9636 | No |
| 🏆 **6) Short Holding (10-Days)** | **4613.46%** | **116.37%** | **3.325** | **-15.03%** | **1,919** | **1.647** | **54.66%** | **0.1162** | **No** |
| **Passive S&P 500 Buy & Hold** | 78.12% | 12.26% | 0.908 | -20.35% | 581 | 12.683 | 78.83% | 0.1397 | No |

---

## 📉 Out-of-Sample Performance (2021–2026)

Evaluated over the strict validation period. Next-day open execution ($T+1$) is utilized for active strategies to eliminate look-ahead bias.

| Variant | Cumulative Return | Ann. Return | Sharpe Ratio | Max Drawdown | Total Trades | Profit Factor | Win Rate | Runs Test p-value | Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1) Baseline (SUE 1.5, Vol 1.5, SL 5%)** | 1379.41% | 66.17% | 2.531 | -23.84% | 2,284 | 1.878 | 53.33% | 0.2175 | No |
| **2) Aggressive SUE (SUE 1.0)** | 1006.52% | 57.31% | 2.508 | -17.54% | 3,353 | 1.756 | 51.57% | 0.0567 | No |
| **3) Conservative SUE (SUE 2.0)** | 2406.49% | 83.53% | 2.715 | -23.71% | 1,581 | 1.917 | 53.32% | 0.0230 | Yes |
| **4) Without Volume Filter** | 1078.85% | 59.20% | 2.452 | -20.16% | 3,418 | 1.979 | 53.31% | 0.4231 | No |
| **5) Without Stop Loss** | 831.61% | 52.29% | 2.171 | -19.84% | 2,282 | 2.087 | 60.39% | 0.9611 | No |
| 🏆 **6) Short Holding (10-Days)** | **9356.99%** | **135.72%** | **2.930** | **-22.86%** | **2,310** | **2.088** | **58.44%** | **0.0189** | **Yes** |
| **Passive S&P 500 Buy & Hold** | 104.30% | 14.41% | 0.855 | -21.74% | 598 | 10.698 | 70.90% | 0.2328 | No |
