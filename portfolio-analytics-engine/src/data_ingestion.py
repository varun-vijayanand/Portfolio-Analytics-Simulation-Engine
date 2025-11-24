import yfinance as yf
import pandas as pd
import os
from datetime import datetime

RAW_DATA_PATH = "data/raw/"
REFERENCE_DATA_PATH = "data/reference/"

os.makedirs(RAW_DATA_PATH, exist_ok=True)


class DataIngestion:
    """Handles downloading and loading all required portfolio & market data."""

    def load_portfolio_data(self, file_path):
        """Load portfolio CSV (tickers + weights)."""
        return pd.read_csv(file_path)

    def fetch_market_data(self, tickers, start, end):
        """Download adjusted daily OHLCV price data."""
        print(f"Downloading price data for: {tickers}")

        data = yf.download(
            tickers,
            start=start,
            end=end,
            auto_adjust=False,
            group_by='ticker'
        )

        # ===== FIX: Extract only Adj Close and flatten the columns =====
        if isinstance(data.columns, pd.MultiIndex):
            try:
                data = data.xs('Adj Close', axis=1, level=1)
                data.columns.name = None
            except Exception:
                raise ValueError(
                    "Failed to extract Adj Close. "
                    "YFinance returned unexpected multi-index structure."
                )

        # If single-ticker, rename column to ticker name
        if len(tickers) == 1 and "Adj Close" in data.columns:
            data = data.rename(columns={"Adj Close": tickers[0]})

        out = os.path.join(RAW_DATA_PATH, "market_price_data.csv")
        data.to_csv(out)
        print("Saved:", out)

        return data

    def download_benchmark(self):
        """Download S&P 500 data."""
        benchmark = "^GSPC"
        print("Downloading benchmark:", benchmark)

        data = yf.download(benchmark, start="2015-01-01")

        out = os.path.join(RAW_DATA_PATH, "benchmark_data.csv")
        data.to_csv(out)
        print("Saved:", out)

        return data

    def download_corporate_actions(self, tickers):
        """Download dividends and splits."""
        corp_actions = {}

        for t in tickers:
            print(f"Downloading corporate actions for {t}")
            stock = yf.Ticker(t)

            dividends = stock.dividends
            splits = stock.splits

            corp_actions[t] = {
                "dividends": dividends,
                "splits": splits
            }

            dividends.to_csv(os.path.join(RAW_DATA_PATH, f"{t}_dividends.csv"))
            splits.to_csv(os.path.join(RAW_DATA_PATH, f"{t}_splits.csv"))

        return corp_actions

    def download_fama_french(self):
        """Download Fama-French 3 factors."""
        print("Downloading Fama-French 3 Factor data...")

        url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
        df = pd.read_csv(url, skiprows=3)

        df = df.rename(columns={"Unnamed: 0": "date"})
        df = df.dropna()
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

        out = os.path.join(RAW_DATA_PATH, "fama_french.csv")
        df.to_csv(out, index=False)
        print("Saved:", out)

        return df

    def download_risk_free(self):
        """Download US 3M T-bill (risk-free rate)."""
        print("Downloading risk-free rate (13-week T-bill)...")

        t_bill = yf.download("^IRX", start="2015-01-01")

        out = os.path.join(RAW_DATA_PATH, "risk_free_rate.csv")
        t_bill.to_csv(out)

        print("Saved:", out)
        return t_bill
