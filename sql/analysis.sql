-- average annual return and volatility by sector
WITH stats AS (
    SELECT ticker,
           AVG(ret) * 252 AS ann_ret,
           STDDEV_SAMP(ret) * SQRT(252) AS ann_vol
    FROM daily_returns
    WHERE ret IS NOT NULL
    GROUP BY ticker
)
SELECT a.sector,
       COUNT(*) AS n,
       ROUND(AVG(s.ann_ret)::numeric, 3) AS avg_ret,
       ROUND(AVG(s.ann_vol)::numeric, 3) AS avg_vol
FROM stats s
JOIN asset a USING (ticker)
GROUP BY a.sector
ORDER BY avg_vol DESC;

-- every stock ranked by its worst peak-to-trough loss
SELECT ticker, MIN(drawdown) AS max_dd,
       RANK() OVER (ORDER BY MIN(drawdown)) AS worst
FROM drawdowns
GROUP BY ticker;
