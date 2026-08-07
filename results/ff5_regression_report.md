# 📐 Régression Fama-French 5 Facteurs — PST_012 PEAD Strategy

Ce rapport teste si l'alpha de la stratégie PEAD (Variante 6, Holding 10J) survit après contrôle pour les 5 facteurs de risque systématique de Fama & French (2015) :
MKT-RF (marché), SMB (taille), HML (value), RMW (profitabilité), CMA (investissement).

**Modèle** : $R_{PEAD,t} - R_{f,t} = \alpha + \beta_1 MKT_t + \beta_2 SMB_t + \beta_3 HML_t + \beta_4 RMW_t + \beta_5 CMA_t + \epsilon_t$

**Erreurs standards** : Robustes à l'hétéroscédasticité (HC1 / White)

---

## Résultats de la Régression

| Période | Alpha Ann. | t-stat (α) | p-value (α) | β MKT | β SMB | β HML | β RMW | β CMA | R² adj. | N obs. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Full Period (2015-2026) | 67.13% *** | 8.864 | 0.0000 | +0.819 | +0.103 | +0.059 | +0.065 | -0.187 | 0.274 | 2847 |
| In-Sample (2015-2020) | 58.07% *** | 6.029 | 0.0000 | +0.770 | +0.125 | +0.053 | -0.024 | -0.270 | 0.296 | 1510 |
| Out-of-Sample (2021-2026) | 76.07% *** | 6.472 | 0.0000 | +0.910 | +0.072 | +0.108 | +0.113 | -0.162 | 0.255 | 1337 |

## Interprétation Académique

- **Alpha significatif (p < 0.05)** → L'anomalie PEAD génère un rendement excédentaire **au-delà** de ce que les facteurs de risque systématique expliquent. L'alpha ne provient pas d'une exposition implicite au marché, à la taille, au value, à la profitabilité ou à l'investissement.
- **R² faible** → La stratégie a une faible corrélation avec les facteurs traditionnels, ce qui confirme son caractère **event-driven** et non factoriel.
- **β MKT de ~0.8 à 0.9** → La stratégie présente une exposition importante au marché (bêta proche de 1.0), ce qui est cohérent avec son profil long-only (achats uniquement). Cependant, l'alpha résiduel après correction de cette exposition reste extrêmement élevé et significatif.

## Référence

Fama, E. F., & French, K. R. (2015). *A five-factor asset pricing model*. Journal of Financial Economics, 116(1), 1-22.
