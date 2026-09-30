import os
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine

sectors = {
    "AAPL": "Information Technology", "MSFT": "Information Technology", "NVDA": "Information Technology",
    "ORCL": "Information Technology", "CSCO": "Information Technology", "INTC": "Information Technology",
    "IBM": "Information Technology", "ADBE": "Information Technology", "QCOM": "Information Technology",
    "TXN": "Information Technology", "ACN": "Information Technology",
    "GOOGL": "Communication Services", "META": "Communication Services", "VZ": "Communication Services",
    "T": "Communication Services", "CMCSA": "Communication Services", "DIS": "Communication Services",
    "NFLX": "Communication Services",
    "AMZN": "Consumer Discretionary", "HD": "Consumer Discretionary", "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary", "SBUX": "Consumer Discretionary", "LOW": "Consumer Discretionary",
    "BKNG": "Consumer Discretionary",
    "PG": "Consumer Staples", "KO": "Consumer Staples", "PEP": "Consumer Staples", "WMT": "Consumer Staples",
    "COST": "Consumer Staples", "MO": "Consumer Staples", "CL": "Consumer Staples", "MDLZ": "Consumer Staples",
    "JNJ": "Health Care", "UNH": "Health Care", "PFE": "Health Care", "MRK": "Health Care",
    "ABT": "Health Care", "TMO": "Health Care", "AMGN": "Health Care", "LLY": "Health Care",
    "BMY": "Health Care", "GILD": "Health Care", "MDT": "Health Care", "DHR": "Health Care",
    "JPM": "Financials", "BAC": "Financials", "WFC": "Financials", "C": "Financials", "GS": "Financials",
    "MS": "Financials", "BLK": "Financials", "AXP": "Financials", "USB": "Financials", "BK": "Financials",
    "COF": "Financials", "MET": "Financials",
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "CAT": "Industrials", "HON": "Industrials", "UNP": "Industrials", "UPS": "Industrials",
    "LMT": "Industrials", "BA": "Industrials", "EMR": "Industrials", "FDX": "Industrials", "DE": "Industrials",
    "NEE": "Utilities", "DUK": "Utilities", "SO": "Utilities",
    "SPG": "Real Estate", "AMT": "Real Estate",
}

engine = create_engine(f"postgresql+psycopg2://postgres:{os.environ['PGPASSWORD']}@localhost:5432/rmt")

raw = yf.download(list(sectors), start="2016-09-26", end="2026-09-26", auto_adjust=True, progress=False)["Close"]
px = raw.dropna(axis=1, thresh=int(0.98 * len(raw))).ffill().dropna()

prices = px.reset_index().melt(id_vars="Date", var_name="ticker", value_name="close")
prices.columns = ["date", "ticker", "close"]
assets = pd.DataFrame({"ticker": px.columns, "sector": [sectors[t] for t in px.columns]})

assets.to_sql("asset", engine, if_exists="append", index=False)
prices.to_sql("prices", engine, if_exists="append", index=False, chunksize=10000)

print(px.shape)
print("dropped:", sorted(set(sectors) - set(px.columns)))
