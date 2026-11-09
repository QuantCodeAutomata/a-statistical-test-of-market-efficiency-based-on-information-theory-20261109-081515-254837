# A statistical test of market efficiency based on information theory

Replication of the empirical application (Section 4, "Empirical study") of
*A statistical test of market efficiency based on information theory*
(Fiedor, 2022 — arXiv:2208.11976).

The paper defines an entropy-based market-information estimator
![I-hat](https://render.githubusercontent.com/render/math?math=%5Cwidehat%7BI%7D%5E%7BL%2B1%7D)
of order `L` that measures the deviation of a binary price-return series from
a memoryless (efficient) process, and a statistical test of the efficient
market hypothesis (EMH) built on the asymptotic distribution of this
estimator. This repository reproduces the paper's Section 4 empirical study:
the estimator with `L = 1`, computed in a rolling window of `n = 100`
observations, applied to four real daily-price series of 2021 — the CAC 40
index, the Russell 2000 index, the Perficient (PRFT) stock, and the BTC/USD
cryptocurrency pair — and tested for EMH rejection at the 95%, 99%, and 99.9%
confidence levels.

## Repository layout

```
src/     market-information estimator (market_information.py), the
         statistical test (efficiency_test.py), and experiment parameters
         (config.py)
exp/     exp4.py — the empirical application experiment
data/    data_loader.py — OHLCV bars through the QuantX Dataloader REST API
tests/   unit tests (synthetic fixtures) and market-data tests (reduced,
         cached real-data slice)
results/ tables, plots, logs, and RESULTS.md (paper comparison)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATALOADER_API_KEY and MASSIVE_API_KEY
```

`DATALOADER_API_KEY` (QuantX Dataloader, https://quantx.limex.pro/) and
`MASSIVE_API_KEY` (Massive, https://massive.com/) are required to download
the price series; both keys are read from the environment and are never
written to any file in this repository.

## Running the experiment

```bash
python -m exp.exp4
```

This downloads daily prices for 2021 (CAC 40, Russell 2000, Perficient,
BTC/USD) through the QuantX Dataloader, computes the rolling market
information and the EMH rejection table at each date, and writes to
`results/`:

- `exp4_summary.csv` — per-asset sample size, date range, mean
  ![I2](https://render.githubusercontent.com/render/math?math=%5Cwidehat%7BI%7D%5E2),
  and percentage of dates with EMH rejection at each confidence level;
- `exp4_series_<asset>.csv` — the full per-date market-information and
  rejection series for each asset;
- `exp4_market_information.png` — the market information over time for each
  asset with the 95%/99%/99.9% rejection thresholds;
- `exp4_log.json` — data-load metadata (tickers, data source, warnings) and
  the thresholds used.

## Tests

```bash
python -m pytest -m "not market_data"   # synthetic-fixture unit tests only
python -m pytest                        # also runs the market-data tests
                                         # (needs DATALOADER_API_KEY/MASSIVE_API_KEY)
```

Unit tests check the properties the paper states: the estimator is
non-negative, the binary-return rule classifies flat and falling prices as 0,
the rolling window introduces no look-ahead, and the test's critical values
follow Gamma(2^(L-1), 1/(ln(2)·n)) (paper, Eq. (11)) and increase with the
confidence level. The market-data tests use a short, cached real-data slice
and check the same properties plus the directional finding that mixing many
stocks into an index lowers exploitable market information relative to one
of its constituents.

## Reproduce everything

```bash
./reproduce.sh
```

Runs the full test suite and the experiment with the commands above.

See `results/RESULTS.md` for the comparison with the paper's reported
figures, data-source deviations, and anything not reproduced.
