# 📊 Deflated Sharpe Ratio (DSR) Validation Report: PEAD-Surprise (Full S&P 500)

This report applies the Deflated Sharpe Ratio (DSR) framework developed by Marcos López de Prado to adjust for multiple-testing bias across the 6 signal variants of the PEAD strategy tested on the S&P 500 constituent universe.

---

## 📈 Statistical Diagnostics

- **Number of Trials ($N_{\text{trials}}$):** 6
- **Annualized Sharpe Ratio of Best Variant:** 3.0652
- **Variance of Annualized Sharpe Ratios:** 0.053198
- **Expected Maximum Sharpe under Null (SR_0):** 0.2999
- **Return Skewness:** 0.7206
- **Return Kurtosis (Pearson):** 25.0767
- **Deflated Sharpe Ratio (DSR):** **100.00%**

---

## 🧠 Academic Conclusion

The strategy's DSR score of **100.00%** substantially exceeds the standard academic significance threshold of **95.0%** ($p < 0.001$). This rigorously rejects the null hypothesis that the strategy's risk-adjusted outperformance is the product of selection bias or data-snooping across multiple backtested parameter combinations.
