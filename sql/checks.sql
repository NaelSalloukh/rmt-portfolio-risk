-- total rows: 2,514 days x 73 tickers = 183,522
SELECT COUNT(*) FROM prices;

-- every ticker should have the full 2,514 rows
SELECT ticker, MIN(date), MAX(date), COUNT(*) AS total_count
FROM prices
GROUP BY ticker
ORDER BY total_count
LIMIT 5;

-- all 10 sectors present
SELECT sector, COUNT(*) AS n
FROM asset
GROUP BY sector
ORDER BY n DESC;

-- first return per ticker is NULL, the rest are small daily moves
SELECT * FROM daily_returns WHERE ticker = 'AAPL' ORDER BY date LIMIT 5;

-- AAPL volatility should spike in March 2020
SELECT * FROM rolling_vol WHERE ticker = 'AAPL' AND date BETWEEN '2020-03-01' AND '2020-03-31';
