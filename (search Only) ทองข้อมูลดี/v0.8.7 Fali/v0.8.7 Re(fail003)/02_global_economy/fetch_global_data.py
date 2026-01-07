import yfinance as yf
import pandas as pd
import os

# --- CONFIG ---
DATA_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\02_global_economy\data"
os.makedirs(DATA_DIR, exist_ok=True)

# The "Global Brute Force" List
ASSETS = {
    # --- INDICES ---
    "SP500_US": "^GSPC",
    "Nikkei_Japan": "^N225",
    "FTSE_UK": "^FTSE",
    "DAX_Germany": "^GDAXI",
    "Shanghai_China": "000001.SS",
    "Sensex_India": "^BSESN",
    # --- FOREX ---
    "EUR_USD": "EURUSD=X",
    "JPY_USD": "JPY=X",
    # --- COMMODITIES ---
    "Gold": "GC=F",
    "Oil_WTI": "CL=F",
    # --- CRYPTO ---
    "Bitcoin": "BTC-USD",
}


def fetch_data():
    print(f"--- GLOBAL DATA ACQUISITION STARTED ---")
    print(f"Target Directory: {DATA_DIR}")

    summary = []

    for name, ticker in ASSETS.items():
        print(f"Fetching {name} ({ticker})...")
        try:
            # Download max history
            df = yf.download(ticker, period="max", progress=False)

            if df.empty:
                print(f"   WARNING: No data found for {ticker}")
                summary.append({"name": name, "status": "EMPTY", "rows": 0})
                continue

            # Clean Index
            df.index.name = "Date"
            df.reset_index(inplace=True)

            # Save Raw
            save_path = os.path.join(DATA_DIR, f"{name}.csv")
            df.to_csv(save_path, index=False)

            rows = len(df)
            print(f"   SUCCESS: {rows} rows saved to {save_path}")
            summary.append({"name": name, "status": "PASS", "rows": rows})

        except Exception as e:
            print(f"   FAILED: {e}")
            summary.append({"name": name, "status": "FAIL", "error": str(e)})

    # Summary Report
    print("\n--- ACQUISITION SUMMARY ---")
    summary_df = pd.DataFrame(summary)
    print(summary_df)
    summary_df.to_csv(os.path.join(DATA_DIR, "_acquisition_summary.csv"), index=False)


if __name__ == "__main__":
    fetch_data()
