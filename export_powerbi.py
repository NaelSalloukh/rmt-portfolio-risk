"""Export backtest results as flat CSV files for the Power BI dashboard."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.data import load_returns
from src.backtest import backtest, summary

out = Path("powerbi/data")
out.mkdir(parents=True, exist_ok=True)
R, _ = load_returns()
daily, rebal, summ = [], [], []
for label, long in [("short positions allowed", False), ("long-only", True)]:
    rets, info = backtest(R, long=long)
    d = rets.rename_axis("date").reset_index().melt("date", var_name="method", value_name="return")
    d = d.sort_values(["method", "date"])
    g = d.groupby("method")["return"]
    d["growth of $1"] = g.transform(lambda r: (1 + r).cumprod())
    d["rolling vol"] = g.transform(lambda r: r.rolling(252).std() * np.sqrt(252))
    s = summary(rets, info).rename_axis("method").reset_index()
    for df in (d, info, s):
        df.insert(0, "portfolio", label)
    daily.append(d)
    rebal.append(info)
    summ.append(s)
pd.concat(daily).to_csv(out / "daily.csv", index=False)
pd.concat(rebal).to_csv(out / "rebalances.csv", index=False)
pd.concat(summ).round(4).to_csv(out / "summary.csv", index=False)
print("saved to", out.resolve())
