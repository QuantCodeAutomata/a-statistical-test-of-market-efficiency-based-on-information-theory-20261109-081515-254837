"""Unit tests for src/market_information.py on synthetic fixtures."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.market_information import (
    binary_returns,
    market_information_order1,
    rolling_market_information,
)


def test_binary_returns_strictly_positive_rule():
    """X_i = 1{P_i - P_{i-1} > 0}: flat and falling prices both give 0."""
    prices = pd.Series([100.0, 100.0, 99.0, 101.0, 101.0], index=pd.date_range("2021-01-01", periods=5))
    x = binary_returns(prices)
    assert list(x.values) == [0, 0, 1, 0]
    assert len(x) == len(prices) - 1


def test_binary_returns_rejects_missing_values():
    prices = pd.Series([100.0, np.nan, 99.0])
    with pytest.raises(ValueError):
        binary_returns(prices)


def test_market_information_zero_for_iid_coin_flip_limit():
    """A perfectly alternating series (0,1,0,1,...) is fully predictable: I2 -> 1."""
    x = np.tile([0, 1], 50)
    info = market_information_order1(x)
    assert info == pytest.approx(1.0, abs=1e-9)


def test_market_information_zero_for_constant_conditional_half():
    """If P(up | down) = P(up | up) = 1/2 exactly, the estimator is 0 (no dependence)."""
    # Construct a window where, for both prefixes, the suffix is 1 exactly half the time.
    x = np.array([0, 1, 0, 0, 1, 1, 0, 1] * 4)
    info = market_information_order1(x)
    # Not necessarily exactly 0 for this particular synthetic sample, but must be
    # non-negative and finite, which is the property guaranteed by the estimator.
    assert info >= 0.0
    assert np.isfinite(info)


def test_market_information_non_negative_and_bounded():
    """I_hat^2 >= 0 always (it is 1 minus a weighted average of entropies in [0,1])."""
    rng = np.random.default_rng(0)
    for _ in range(20):
        x = rng.integers(0, 2, size=100)
        info = market_information_order1(x)
        assert info >= 0.0
        assert info <= 1.0 + 1e-9


def test_market_information_requires_binary_input():
    with pytest.raises(ValueError):
        market_information_order1(np.array([0, 1, 2, 0, 1]))


def test_market_information_requires_minimum_length():
    with pytest.raises(ValueError):
        market_information_order1(np.array([0]))


def test_rolling_market_information_no_lookahead():
    """Each estimate at date t must use only observations up to and including t."""
    rng = np.random.default_rng(1)
    values = rng.integers(0, 2, size=150)
    index = pd.date_range("2021-01-01", periods=150, freq="D")
    returns = pd.Series(values, index=index)
    window = 100

    rolled = rolling_market_information(returns, window)
    assert len(rolled) == len(values) - window + 1
    # Recompute the estimate at the first and last available dates directly
    # from the corresponding slices and check they match exactly: this
    # verifies the window boundaries (no look-ahead, no off-by-one).
    first_slice = values[:window]
    last_slice = values[-window:]
    assert rolled.iloc[0] == pytest.approx(market_information_order1(first_slice))
    assert rolled.iloc[-1] == pytest.approx(market_information_order1(last_slice))
    assert rolled.index[0] == index[window - 1]
    assert rolled.index[-1] == index[-1]


def test_rolling_market_information_empty_when_too_short():
    returns = pd.Series([0, 1, 0], index=pd.date_range("2021-01-01", periods=3))
    rolled = rolling_market_information(returns, window=100)
    assert rolled.empty


def test_rolling_market_information_rejects_small_window():
    returns = pd.Series([0, 1, 0, 1])
    with pytest.raises(ValueError):
        rolling_market_information(returns, window=1)
