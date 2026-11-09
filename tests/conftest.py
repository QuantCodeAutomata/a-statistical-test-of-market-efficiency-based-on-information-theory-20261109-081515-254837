"""Shared pytest fixtures.

Registers the ``market_data`` marker for tests that call the live QuantX
Dataloader API, and caches a reduced price panel across the session so
repeated test runs do not re-download it.
"""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "market_data: test needs DATALOADER_API_KEY/MASSIVE_API_KEY and network access"
    )


@pytest.fixture(scope="session")
def reduced_price_panel(request: pytest.FixtureRequest):
    """A short, cached slice of the real price panel used by Experiment 4.

    Loads two business months of 2021 (instead of the full year) for all four
    assets through ``data/data_loader.py``, so the market-information window
    used in these tests is proportionally shorter (n=20 instead of n=100).
    Skipped when DATALOADER_API_KEY is not set.
    """
    if not os.environ.get("DATALOADER_API_KEY") or not os.environ.get("MASSIVE_API_KEY"):
        pytest.skip("DATALOADER_API_KEY/MASSIVE_API_KEY not set; skipping market-data test")

    cache_dir = request.config.cache.mkdir("exp4_reduced_panel")
    cache_file = cache_dir / "prices.json"
    import json

    import pandas as pd

    if cache_file.exists():
        raw = json.loads(cache_file.read_text())
        return {name: pd.Series(values, index=pd.to_datetime(idx)) for name, (idx, values) in raw.items()}

    from data.data_loader import load_price_panel

    tickers = {
        "CAC 40": "CAC.PA",
        "Russell 2000": "IWM",
        "Perficient": "PRFT",
        "BTC/USD": "X:BTCUSD",
    }
    prices, _ = load_price_panel(
        tickers,
        "2021-01-01",
        "2021-02-28",
        identity_date="2021-12-31",
        equity_names=("CAC 40", "Russell 2000", "Perficient"),
        crypto_names=("BTC/USD",),
    )
    raw = {
        name: (series.index.astype(str).tolist(), series.to_list())
        for name, series in prices.items()
    }
    cache_file.write_text(json.dumps(raw))
    return prices
