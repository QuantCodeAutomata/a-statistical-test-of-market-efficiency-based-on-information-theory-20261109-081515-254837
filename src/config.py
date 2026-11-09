"""Parameters for the empirical application of the market-efficiency test.

All module-level variables below are the parameters used by the experiment in
``exp/exp4.py``. Each has a short note on its meaning, unit, and source
(the paper's section, or "not specified in the paper").
"""

# --- Experiment 4: empirical application to real financial time series ---
# Section 4 ("Empirical study") of the paper.

# Order of the Markov dependence tested, L. The empirical study (Section 4)
# fixes L = 1, the simplest non-trivial order.
L_ORDER = 1

# Rolling-window length n, in observations (business days for the stock
# series, calendar days for BTC/USD). Section 4: "we focus on a particular
# setting with L = 1 and n = 100 business days".
WINDOW_N = 100

# Confidence levels at which the EMH is tested at each date (Section 4,
# Figure 6 commentary: 95%, 99%, 99.9%).
CONFIDENCE_LEVELS = (0.95, 0.99, 0.999)

# Sample period. The paper studies "one year of daily data, 2021" (Section 4)
# and reports the market information between end of May 2021 and end of
# December 2021 for the three business-day series, and from 11 April 2021 for
# BTC/USD (Section 4, page 11). The exact start/end dates of the raw price
# downloads are not given beyond "2021"; we download the full calendar year
# 2021 so that the n=100 rolling window has enough history to produce
# estimates from the dates the paper reports.
START_DATE = "2021-01-01"  # paper: "one year of daily data, 2021" (Sec. 4)
END_DATE = "2021-12-31"  # paper reports estimates through "end December 2021"

# Point-in-time date used to resolve each ticker to the security it names
# (Dataloader `identity_date`). Not specified in the paper; set to the last
# date of the 2021 sample period as required when the paper gives no as-of
# date for its universe.
IDENTITY_DATE = "2021-12-31"

# Tickers used to load each of the four series through the QuantX Dataloader.
# The paper studies the CAC 40 index, the Russell 2000 index, the Perficient
# stock (PRFT, a Russell 2000 constituent), and the BTC/USD cryptocurrency
# pair (Section 4). Direct Massive index symbols for the CAC 40 and Russell
# 2000 (I:FCHI, I:RUT) returned "NOT_AUTHORIZED" (no index-data entitlement),
# so the two indices are proxied by the ETFs that track them: "CAC.PA"
# (Amundi CAC 40 UCITS ETF, Euronext Paris) and "IWM" (iShares Russell 2000
# ETF). This substitution is recorded in results/RESULTS.md. Perficient and
# BTC/USD are loaded directly (PRFT, X:BTCUSD).
TICKERS = {
    "CAC 40": "CAC.PA",
    "Russell 2000": "IWM",
    "Perficient": "PRFT",
    "BTC/USD": "X:BTCUSD",
}

# Series for which the Dataloader's Yahoo backstop and dividend adjustment
# make sense (equities/ETFs). BTC/USD is a crypto pair (X: prefix) and is
# loaded as given, without equity-specific preparation (see the
# massive-rest-market-data skill).
EQUITY_SERIES = ("CAC 40", "Russell 2000", "Perficient")
CRYPTO_SERIES = ("BTC/USD",)

# Dividend adjustment for the equity/ETF series. Not discussed in the paper;
# kept at the Dataloader default (dividend-adjusted, total-return) because the
# paper gives no reason to use unadjusted prices.
ADJUST_DIVIDENDS = True

# Price field used to build the binary return series X_i = 1{P_i > P_{i-1}}
# (Section 2, binary-return definition). The paper only speaks of "price
# returns"; the closing price is the natural daily reference price.
PRICE_FIELD = "close"
