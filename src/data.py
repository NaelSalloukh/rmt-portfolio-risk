import os
import pandas as pd
from sqlalchemy import URL, create_engine


def load_returns():
    url = URL.create("postgresql+psycopg2", username="postgres", password=os.environ["PGPASSWORD"],
                     host="localhost", port=5432, database="rmt")
    engine = create_engine(url)
    r = pd.read_sql("SELECT date, ticker, ret FROM daily_returns WHERE ret IS NOT NULL", engine, parse_dates=["date"])
    sec = pd.read_sql("SELECT ticker, sector FROM asset", engine).set_index("ticker")["sector"]
    R = r.pivot(index="date", columns="ticker", values="ret").dropna()
    R = R[sec.loc[R.columns].sort_values(kind="stable").index]
    return R, sec.loc[R.columns]
