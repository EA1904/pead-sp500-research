"""
📊 Téléchargement des Données de Résultats (Earnings) via yfinance - S&P 500 Complet
================================================================================
Télécharge les données d'earnings historiques (jusqu'à 100 trimestres / 25 ans)
gratuitement et proprement pour l'ensemble des actions du S&P 500.
"""

import pandas as pd
import yfinance as yf
import time
import os
import sys

DATA_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(DATA_DIR, exist_ok=True)

OUT_PATH = os.path.join(DATA_DIR, "earnings_raw.csv")
SKIPPED_PATH = os.path.join(DATA_DIR, "skipped_tickers.txt")
PRICE_DATA_PATH = r"c:\Users\DELL\Desktop\PHD\New meth\data\sp500_full\ready\sp500_full_ready.parquet"


def main():
    print("Lecture des tickers de l'univers S&P 500...")
    
    tickers = []
    if os.path.exists(PRICE_DATA_PATH):
        try:
            df_prices = pd.read_parquet(PRICE_DATA_PATH, columns=["Ticker"])
            tickers = sorted(df_prices["Ticker"].unique().tolist())
            print(f"Chargé {len(tickers)} tickers depuis le fichier parquet local.")
        except Exception as e:
            print(f"Erreur de lecture du Parquet local: {e}")
            
    if not tickers:
        print("Téléchargement de la liste des constituants actuels du S&P 500 depuis Wikipédia...")
        try:
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            tickers = sorted(table[0]['Symbol'].tolist())
            # Convertir les points en tirets pour yfinance (ex: BRK.B -> BRK-B)
            tickers = [t.replace('.', '-') for t in tickers]
            print(f"Récupéré {len(tickers)} tickers depuis Wikipédia.")
        except Exception as e:
            print(f"Erreur lors du téléchargement de Wikipédia: {e}")
            # Liste de secours
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "LLY", "V"]
            print(f"Utilisation de la liste de secours ({len(tickers)} tickers majeurs).")

    completed_tickers = set()
    all_dfs = []

    # Charger les tickers déjà téléchargés avec succès
    if os.path.exists(OUT_PATH):
        try:
            df_existing = pd.read_csv(OUT_PATH)
            if not df_existing.empty and "symbol" in df_existing.columns:
                completed_tickers = set(df_existing["symbol"].unique().tolist())
                # Grouper par symbole pour conserver les structures propres
                for sym, group in df_existing.groupby("symbol"):
                    all_dfs.append(group)
                print(f"Livrables : {len(completed_tickers)} tickers déjà chargés.")
        except Exception as e:
            print(f"Erreur lors de la lecture des livrables : {e}")

    # Charger les tickers exclus (sans données)
    skipped_tickers = set()
    if os.path.exists(SKIPPED_PATH):
        try:
            with open(SKIPPED_PATH, "r", encoding="utf-8") as f:
                skipped_tickers = set([line.strip() for line in f if line.strip()])
                print(f"Exclusions : {len(skipped_tickers)} tickers à ignorer (pas de données).")
        except Exception as e:
            print(f"Erreur lors de la lecture des exclusions : {e}")

    # Filtrer les tickers restants
    tickers_to_query = [t for t in tickers if t not in completed_tickers and t not in skipped_tickers]
    print(f"Tickers restants à interroger via yfinance : {len(tickers_to_query)}")

    if not tickers_to_query:
        print("Tous les tickers ont déjà été traités.")
        return

    n_total = len(tickers)
    n_processed = len(completed_tickers) + len(skipped_tickers)

    for ticker in tickers_to_query:
        n_processed += 1
        print(f"[{n_processed}/{n_total}] Téléchargement de {ticker}...", end="", flush=True)

        try:
            # Récupérer l'historique d'earnings via yfinance (limite de 100 trimestres)
            yf_ticker = yf.Ticker(ticker)
            df = yf_ticker.get_earnings_dates(limit=100)

            if df is not None and not df.empty:
                # Reset index pour récupérer les dates d'earnings
                df = df.reset_index()
                # Renommer les colonnes pour correspondre au schéma attendu
                df = df.rename(columns={
                    "Earnings Date": "date",
                    "Reported EPS": "epsActual",
                    "EPS Estimate": "epsEstimated"
                })
                # Ajouter le symbole
                df["symbol"] = ticker
                # Formater la date en YYYY-MM-DD local (sans timezone)
                df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
                
                # Conserver uniquement les colonnes requises
                df_clean = df[["symbol", "date", "epsActual", "epsEstimated"]]
                
                all_dfs.append(df_clean)
                completed_tickers.add(ticker)
                print(f" SUCCESS ({len(df_clean)} trimestres)")
            else:
                skipped_tickers.add(ticker)
                with open(SKIPPED_PATH, "a", encoding="utf-8") as sf:
                    sf.write(f"{ticker}\n")
                print(" EMPTY (pas de données)")

        except Exception as e:
            print(f" ERROR : {e}")
            if "HTTP Error" in str(e) or "429" in str(e):
                print("Rate limit détecté. Pause de 10 secondes...")
                time.sleep(10)
            else:
                skipped_tickers.add(ticker)
                with open(SKIPPED_PATH, "a", encoding="utf-8") as sf:
                    sf.write(f"{ticker}\n")

        # Petite pause de politesse pour éviter les blocages de Yahoo Finance
        time.sleep(0.5)

        # Sauvegarde intermédiaire tous les 10 tickers
        if len(completed_tickers) % 10 == 0 and all_dfs:
            df_temp = pd.concat(all_dfs, ignore_index=True)
            df_temp.to_csv(OUT_PATH, index=False)

    # Sauvegarde finale
    if all_dfs:
        df_final = pd.concat(all_dfs, ignore_index=True)
        df_final.to_csv(OUT_PATH, index=False)
        print(f"\nSauvegarde réussie de {len(df_final)} lignes d'earnings pour {len(completed_tickers)} tickers dans {OUT_PATH}")
    else:
        print("\nAucune donnée n'a été récupérée.")


if __name__ == "__main__":
    main()
