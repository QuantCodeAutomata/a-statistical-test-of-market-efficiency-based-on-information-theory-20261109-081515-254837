"""Unit tests for src/efficiency_test.py on synthetic fixtures."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy.stats import gamma

from src.efficiency_test import critical_value, rejection_rates, rejection_table


def test_critical_value_matches_gamma_quantile_n100_L1():
    """Paper, Eq. (11): Gamma(2^(L-1), 1/(ln(2)*n)) with L=1, n=100."""
    n = 100
    expected_95 = gamma.ppf(0.95, a=1, scale=1.0 / (np.log(2.0) * n))
    assert critical_value(0.95, n, L=1) == pytest.approx(expected_95)
    # Published approximate values (paper, Section 4): ~0.0432, ~0.0664, ~0.0997.
    assert critical_value(0.95, n, L=1) == pytest.approx(0.0432, abs=5e-4)
    assert critical_value(0.99, n, L=1) == pytest.approx(0.0664, abs=5e-4)
    assert critical_value(0.999, n, L=1) == pytest.approx(0.0997, abs=5e-4)


def test_critical_value_increases_with_confidence():
    n = 100
    c95 = critical_value(0.95, n)
    c99 = critical_value(0.99, n)
    c999 = critical_value(0.999, n)
    assert c95 < c99 < c999


def test_critical_value_decreases_with_window_length():
    """A larger window shrinks the scale 1/(ln(2)*n), so the threshold falls."""
    small = critical_value(0.95, n=50)
    large = critical_value(0.95, n=200)
    assert large < small


def test_critical_value_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        critical_value(1.5, n=100)
    with pytest.raises(ValueError):
        critical_value(0.0, n=100)


def test_rejection_table_flags_values_above_threshold():
    index = pd.date_range("2021-01-01", periods=5)
    info = pd.Series([0.01, 0.05, 0.07, 0.10, 0.20], index=index)
    table, thresholds = rejection_table(info, n=100, confidence_levels=(0.95, 0.99, 0.999))
    assert set(thresholds) == {0.95, 0.99, 0.999}
    # 0.01 is below every threshold; 0.20 is above every threshold.
    assert not table.loc[index[0], "reject_0.95"]
    assert table.loc[index[4], "reject_0.95"]
    assert table.loc[index[4], "reject_0.999"]


def test_rejection_rates_percentage_in_0_100():
    index = pd.date_range("2021-01-01", periods=4)
    info = pd.Series([0.0, 0.2, 0.2, 0.2], index=index)
    table, _ = rejection_table(info, n=100, confidence_levels=(0.95,))
    rates = rejection_rates(table, (0.95,))
    assert rates[0.95] == pytest.approx(75.0)
    assert 0.0 <= rates[0.95] <= 100.0


def test_rejection_rates_requires_table_columns():
    table = pd.DataFrame({"I2_hat": [0.1, 0.2]})
    with pytest.raises(KeyError):
        rejection_rates(table, (0.95,))
