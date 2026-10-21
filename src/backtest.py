"""Rolling out-of-sample backtest of minimum-variance portfolios built from different covariance estimators."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
from .rmt import clean_cov, eig, min_var, n_signal


def raw_cov(X):
    """Sample covariance matrix of a T x N array of returns."""
    return np.cov(X, rowvar=False)


def lw_cov(X):
    """Ledoit-Wolf shrinkage towards a scaled identity matrix."""
    return LedoitWolf().fit(X).covariance_


def rmt_adj_cov(X):
    """RMT cleaning with the market-adjusted noise edge, which keeps more factors."""
    T, N = X.shape
    w = eig(np.corrcoef(X, rowvar=False))[0]
    return clean_cov(X, n_signal(w, N / T, 1 - w[0] / N))


ESTIMATORS = {"raw": raw_cov, "rmt": clean_cov, "ledoit-wolf": lw_cov}


def long_only(S, cap=0.1):
    """Minimum-variance weights with no short positions and at most `cap` in any one stock."""
    n = len(S)
    A = S / np.trace(S) * n
    res = minimize(lambda w: w @ A @ w, np.full(n, 1 / n), jac=lambda w: 2 * A @ w, method="SLSQP",
                   bounds=[(0, cap)] * n, constraints={"type": "eq", "fun": lambda w: w.sum() - 1},
                   options={"ftol": 1e-12, "maxiter": 1000})
    w = np.clip(res.x, 0, cap)
    return w / w.sum()


def backtest(R, window=252, step=21, long=False, cap=0.1, estimators=ESTIMATORS):
    """Rebalance every `step` days using only the previous `window` days, then hold until the next rebalance.

    Returns daily portfolio returns for each method and a table of what each method did at every rebalance.
    """
    X, dates, N = R.to_numpy(), R.index, R.shape[1]
    rets, info, prev = {m: [] for m in [*estimators, "equal"]}, [], {}
    for t in range(window, len(X), step):
        train, hold = X[t - window:t], X[t:t + step]
        for m in rets:
            S = raw_cov(train) if m == "equal" else estimators[m](train)
            w = np.full(N, 1 / N) if m == "equal" else long_only(S, cap) if long else min_var(S)
            rets[m].append(pd.Series(hold @ w, index=dates[t:t + step]))
            info.append({"date": dates[t], "method": m, "predicted vol": np.sqrt(252 * w @ S @ w),
                         "realised vol": np.sqrt(252) * (hold @ w).std(),
                         "turnover": np.abs(w - prev[m]).sum() if m in prev else np.nan,
                         "effective holdings": 1 / (w ** 2).sum(), "largest weight": np.abs(w).max(),
                         "gross exposure": np.abs(w).sum()})
            prev[m] = w
    return pd.DataFrame({m: pd.concat(r) for m, r in rets.items()}), pd.DataFrame(info)


def summary(rets, info, cost=0.001):
    """One row per method: realised risk, return, drawdown, forecast accuracy and trading activity.

    `cost` is the trading cost per unit of turnover (0.001 = 0.1%), used for the return after costs.
    """
    g = info.groupby("method")
    wealth = (1 + rets).cumprod()
    out = pd.DataFrame({
        "realised vol": rets.std() * np.sqrt(252),
        "annual return": rets.mean() * 252,
        "max drawdown": (wealth / wealth.cummax() - 1).min(),
        "mean predicted vol": g["predicted vol"].mean(),
        "monthly turnover": g["turnover"].mean(),
        "effective holdings": g["effective holdings"].mean(),
        "largest weight": g["largest weight"].mean(),
        "gross exposure": g["gross exposure"].mean(),
    })
    out["return after costs"] = out["annual return"] - cost * 12 * out["monthly turnover"]
    out["realised / predicted"] = out["realised vol"] / out["mean predicted vol"]
    return out.loc[rets.columns]


def bootstrap_vol(a, b, n=2000, block=21, seed=0):
    """Block bootstrap of the difference in annualised volatility between two daily return series, a minus b."""
    a, b = np.asarray(a), np.asarray(b)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(a) - block, (n, len(a) // block))
    idx = (starts[:, :, None] + np.arange(block)).reshape(n, -1)
    d = (a[idx].std(axis=1) - b[idx].std(axis=1)) * np.sqrt(252)
    return {"difference": (a.std() - b.std()) * np.sqrt(252), "95% low": np.quantile(d, 0.025),
            "95% high": np.quantile(d, 0.975), "share of resamples a lower": (d < 0).mean()}
