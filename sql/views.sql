CREATE VIEW daily_returns AS
SELECT date, ticker,
       close / LAG(close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret
FROM prices;

CREATE VIEW rolling_vol AS
SELECT date, ticker,
       STDDEV_SAMP(ret) OVER (PARTITION BY ticker ORDER BY date
                              ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_21d
FROM daily_returns
WHERE ret IS NOT NULL;

CREATE VIEW drawdowns AS
SELECT date, ticker, close,
       close / MAX(close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS drawdown
FROM prices;
