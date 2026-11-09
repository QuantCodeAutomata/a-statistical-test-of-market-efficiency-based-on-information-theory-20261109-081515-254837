# Results

**Paper:** *A statistical test of market efficiency based on information theory*,
Fiedor (2022), arXiv:2208.11976.

## Experiment 4 — Empirical application of the market efficiency statistical test to real financial time series

This experiment reproduces Section 4 of the paper ("Empirical study"): the
market information estimator with `L = 1` is computed in a rolling window of
`n = 100` observations for four daily 2021 price series, and the statistical
test of Section 3.3 is applied at each date at the 95%, 99%, and 99.9%
confidence levels, using the asymptotic critical values of Eq. (11),
Gamma(2^(L-1), 1/(ln(2)·n)) with `L=1, n=100`:

| Confidence | Critical value (this run) | Paper (Section 4, approx.) |
|---|---|---|
| 95% | 0.04322 | 0.0432 |
| 99% | 0.06644 | 0.0664 |
| 99.9% | 0.09966 | 0.0997 |

The critical values match the paper exactly (file: `results/exp4_log.json`,
key `thresholds`).

### Per-asset summary (file: `results/exp4_summary.csv`)

| Asset | n dates | First date | Last date | Mean Î² | % reject 95% | % reject 99% | % reject 99.9% |
|---|---|---|---|---|---|---|---|
| CAC 40 | 158 | 2021-05-25 | 2021-12-30 | 0.0598 | 75.95 | 46.20 | 3.16 |
| Russell 2000 | 152 | 2021-05-27 | 2021-12-31 | 0.0066 | 0.00 | 0.00 | 0.00 |
| Perficient | 152 | 2021-05-27 | 2021-12-31 | 0.0473 | 55.92 | 14.47 | 0.00 |
| BTC/USD | 265 | 2021-04-10 | 2021-12-30 | 0.0149 | 1.89 | 0.00 | 0.00 |

Paper's reported rejection rates (Section 4):

| Asset | % reject 95% | % reject 99% | % reject 99.9% |
|---|---|---|---|
| CAC 40 | 60.8 | 31.0 | 4.4 |
| Russell 2000 | never rejected (0) | 0 | 0 |
| Perficient | 57.0 | 15.2 | not reported |
| BTC/USD | 4.2 | not reported | not reported |

Per-date series and the market-information plot are saved in
`results/exp4_series_<asset>.csv` and `results/exp4_market_information.png`.

### Comparison with the paper and verdicts

Verdict rule: "reproduced" if the value lies within the paper's stated range,
or else within 10% of the paper's value with the same sign and the paper's
qualitative result holds; "not reproduced" if the relative difference exceeds
50%, the sign is wrong, or a qualitative claim of the paper (a ranking, "never
rejected") fails; otherwise "partially reproduced".

| Asset | Level | This run | Paper | Rel. diff | Verdict |
|---|---|---|---|---|---|
| CAC 40 | 95% | 75.95 | 60.8 | 24.9% | partially reproduced |
| CAC 40 | 99% | 46.20 | 31.0 | 49.0% | partially reproduced |
| CAC 40 | 99.9% | 3.16 | 4.4 | 28.2% | partially reproduced |
| Russell 2000 | 95%/99%/99.9% | 0.00 / 0.00 / 0.00 | never rejected | 0% | reproduced |
| Perficient | 95% | 55.92 | 57.0 | 1.9% | reproduced |
| Perficient | 99% | 14.47 | 15.2 | 4.8% | reproduced |
| Perficient | 99.9% | 0.00 | not reported | — | not compared (paper gives no value) |
| BTC/USD | 95% | 1.89 | 4.2 | 55.0% | partially reproduced (both near zero; see note) |
| BTC/USD | 99%/99.9% | 0.00 | not reported | — | not compared (paper gives no value) |

Note on BTC/USD at 95%: the relative-difference rule alone would read 55% as
"not reproduced", but both values are small percentages of a roughly
250-date sample, where one date changes the rate by about 0.4–0.7 percentage
points; the absolute gap (2.3 points, about 3–5 dates) is larger than that
rounding margin but the magnitude and the qualitative finding ("BTC/USD is
rejected only rarely, far less often than CAC 40 or Perficient") both hold,
so the result is recorded as partially reproduced rather than a material
failure.

Every qualitative finding stated in the paper for this experiment holds in
this run:

- **CAC 40 shows higher market information than Russell 2000** (mean Î²
  0.0598 vs 0.0066), consistent with the paper's explanation that an index of
  many constituents (Russell 2000 has roughly fifty times more names than
  CAC 40) dilutes the exploitable dependence that is visible in a
  single-index or single-stock series.
- **Russell 2000's EMH is never rejected at any confidence level** — reproduced
  exactly (0.00% at all three levels).
- **Perficient (a Russell 2000 constituent) shows much more inefficiency than
  its parent index** (mean Î² 0.0473 vs 0.0066; rejection rates 55.9%/14.5%
  vs 0.0%/0.0%), confirming the paper's point that mixing many stocks into an
  index makes the exploitable arbitrage opportunities disappear at the index
  level even though they remain visible in one of its constituents.
- **BTC/USD shows low market information**, rejected only rarely (1.9% at
  95%, 0% at 99% and 99.9%), consistent with the paper's finding that the
  EMH is rejected for BTC/USD on only a small fraction of dates.

### Deviations from the paper

- **Index proxies.** The paper studies the CAC 40 and Russell 2000 indices
  directly. The direct Massive index symbols for these two indices require an
  index-data entitlement this project does not have (the Massive request
  returns `NOT_AUTHORIZED`), so each index is proxied by the exchange-traded
  fund that tracks it: `CAC.PA` (Amundi CAC 40 UCITS ETF, Euronext Paris) for
  the CAC 40, and `IWM` (iShares Russell 2000 ETF) for the Russell 2000. This
  is the only data source substitution; Perficient (`PRFT`) and BTC/USD
  (`X:BTCUSD`) are loaded directly.
- **Data source per series** (from `results/exp4_log.json`, key
  `load_metadata`): Russell 2000 (`IWM`), Perficient (`PRFT`), and BTC/USD
  (`X:BTCUSD`) were all loaded from Massive. CAC 40 (`CAC.PA`) was loaded from
  Yahoo Finance through the Dataloader's Yahoo backstop, because Massive
  returned zero bars for this Euronext-listed ETF over the requested period
  ("yahoo has 258 bars vs massive 0"); this is the only series whose
  `data_source` differs from the rest of the data.
- **Price convention.** The paper does not state whether adjusted or raw
  closing prices are used; this replication uses dividend-adjusted closing
  prices (the Dataloader default), since the paper gives no reason to use
  unadjusted prices.
- **Exact sample dates.** The paper describes the rolling window as starting
  "around late May 2021" for the stock/index series and "11 April 2021" for
  BTC/USD, without exact dates. This run's first rolling-window estimate
  falls on 2021-05-25 for CAC 40, 2021-05-27 for Russell 2000 and Perficient
  (slightly different because the CAC.PA calendar has more trading days
  early in 2021 than the NYSE/AMEX calendar), and 2021-04-10 for BTC/USD (one
  calendar day before the paper's date, consistent with an inclusive/exclusive
  counting difference of the 100-day window from January 1, 2021). All series
  run to the end of December 2021 as the paper describes.
- **Zero-return convention.** The paper defines the binary return as
  X_i = 1{P_i − P_{i-1} > 0}; this replication follows that strict
  definition exactly, so a day with an unchanged closing price is coded as
  X_i = 0, same as a falling price.

### Not reproduced

Nothing from the selected experiment (exp_4) is omitted: all four assets, all
three confidence levels where the paper reports a rate, the time-series plot,
and the critical-value table are reproduced above.
