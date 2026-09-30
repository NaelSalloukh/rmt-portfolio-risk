CREATE TABLE asset (
    ticker VARCHAR(10) PRIMARY KEY,
    sector VARCHAR(40) NOT NULL
);

CREATE TABLE prices (
    date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL REFERENCES asset(ticker),
    close DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (date, ticker)
);

CREATE INDEX idx_prices_ticker_date ON prices (ticker, date);
