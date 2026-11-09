# AGENTS.md

Guide for coding agents and contributors working in this repository.

## What this implements

A reproduction of Section 4 ("Empirical study") of *A statistical test of
market efficiency based on information theory* (Fiedor, 2022,
arXiv:2208.11976): the entropy-based market-information estimator Î² (order
`L = 1`) in a rolling window of `n = 100` observations, and the statistical
test of the efficient market hypothesis (EMH) built on its asymptotic
Gamma(2^(L-1), 1/(ln(2)·n)) distribution, applied to four real 2021 daily
price series (CAC 40, Russell 2000, Perficient, BTC/USD).

## Layout

```
src/     market_information.py (estimator), efficiency_test.py (statistical
         test), config.py (all experiment parameters, module-level constants)
exp/     exp4.py — the empirical-application experiment (python -m exp.exp4)
data/    data_loader.py — OHLCV bars through the QuantX Dataloader REST API
tests/   pytest tests: synthetic-fixture unit tests plus market_data-marked
         tests on a cached, reduced real-data slice
results/ tables, plots, logs, and RESULTS.md (paper comparison)
```

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATALOADER_API_KEY and MASSIVE_API_KEY

python -m pytest -m "not market_data"   # unit tests, no network/credentials
python -m pytest                        # also runs market_data tests

python -m exp.exp4                      # the paper's full 2021 configuration
./reproduce.sh                          # tests + experiment, same commands
```

## Conventions

- All experiment parameters live in `src/config.py` as module-level
  UPPER_CASE variables, each with a one-line comment on its meaning, unit,
  and source (a paper section, or "not specified in the paper"). No classes
  or parameter dicts.
- Market data is loaded only through `data/data_loader.py`
  (`load_ohlcv`, `load_price_panel`), itself backed only by the QuantX
  Dataloader REST API (`https://quantx-api.limex.pro/apis/dataloader`,
  `POST /fetch-ohlcvs`). No other module fetches data directly. Downloaded
  bars are cached under `data/cache/` (git-ignored) and never committed.
- `DATALOADER_API_KEY` and `MASSIVE_API_KEY` are read from the environment
  (`.env`, never committed); `.env.example` holds only empty placeholders.
- Tests: fixtures and the small synthetic series used by unit tests are
  generated inline in the test modules; the market-data tests use a single
  session-scoped, disk-cached fixture (`tests/conftest.py::reduced_price_panel`)
  that loads a two-month, four-asset slice through `data/data_loader.py` and
  is skipped automatically when the API keys are not set. They check the
  paper's properties (non-negativity, no look-ahead, critical-value
  monotonicity, the index-vs-constituent ranking), not its reported numbers.
- Running `python -m exp.exp4` again overwrites every file in `results/`
  (`exp4_summary.csv`, `exp4_series_*.csv`, `exp4_market_information.png`,
  `exp4_log.json`). After a rerun, check the new files and update the
  comparison numbers and verdicts in `results/RESULTS.md` by hand; they are
  not regenerated automatically.
