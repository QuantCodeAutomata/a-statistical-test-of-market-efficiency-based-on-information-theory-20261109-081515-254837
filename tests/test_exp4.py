"""Tests of Experiment 4's methodology on a reduced, real-data price panel.

These tests use market data (through ``reduced_price_panel`` in
``tests/conftest.py``) and are skipped automatically when
``DATALOADER_API_KEY``/``MASSIVE_API_KEY`` are not set.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.efficiency_test import critical_value, rejection_rates, rejection_table
from src.market_information import binary_returns, rolling_market_information

REDUCED_WINDOW = 20  # proportionally shorter than the paper's n=100 (Sec. 4)


@pytest.mark.market_data
def test_russell_2000_has_lower_mean_information_than_perficient(reduced_price_panel):
    """Mixing many stocks in an index should reduce exploitable information
    relative to one of its constituents (paper, Section 4 discussion)."""
    index_returns = binary_returns(reduced_price_panel["Russell 2000"])
    stock_returns = binary_returns(reduced_price_panel["Perficient"])

    index_info = rolling_market_information(index_returns, REDUCED_WINDOW)
    stock_info = rolling_market_information(stock_returns, REDUCED_WINDOW)

    assert not index_info.empty and not stock_info.empty
    assert index_info.mean() <= stock_info.mean() + 1e-6


@pytest.mark.market_data
def test_rolling_information_non_negative_on_real_data(reduced_price_panel):
    for name, prices in reduced_price_panel.items():
        returns = binary_returns(prices)
        info = rolling_market_information(returns, REDUCED_WINDOW)
        assert not info.empty, f"{name}: empty rolling series"
        assert (info >= 0.0).all(), f"{name}: negative market information found"
        assert np.isfinite(info).all()


@pytest.mark.market_data
def test_rejection_rate_is_a_valid_percentage_on_real_data(reduced_price_panel):
    for name, prices in reduced_price_panel.items():
        returns = binary_returns(prices)
        info = rolling_market_information(returns, REDUCED_WINDOW)
        table, _ = rejection_table(info, REDUCED_WINDOW, (0.95, 0.99, 0.999))
        rates = rejection_rates(table, (0.95, 0.99, 0.999))
        for level, rate in rates.items():
            assert 0.0 <= rate <= 100.0, f"{name} @ {level}: invalid rejection rate {rate}"
        # Rejection at a higher confidence level can never be more frequent.
        assert rates[0.999] <= rates[0.99] + 1e-9 <= rates[0.95] + 1e-9


@pytest.mark.market_data
def test_window_length_reduced_proportionally(reduced_price_panel):
    """Sanity check: the reduced test window is shorter than the paper's n=100,
    consistent with the shorter sample loaded for testing."""
    assert REDUCED_WINDOW < 100
    threshold_small = critical_value(0.95, REDUCED_WINDOW)
    threshold_paper = critical_value(0.95, 100)
    assert threshold_small > threshold_paper  # smaller n => larger critical value
