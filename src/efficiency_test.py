"""Statistical test of market efficiency (paper, Section 3.3).

Under the null hypothesis of an efficient market (pi_i^L = 1/2 for every
prefix i), the estimator I_hat^{L+1} follows asymptotically a gamma
distribution Gamma(k, theta) with shape k = 2^(L-1) and scale
theta = 1 / (ln(2) * n) (paper, Eq. (11) and the discussion in Section 3.2.2).
``scipy.stats.gamma`` already implements this distribution's quantile
function, so the asymptotic critical values below are obtained directly from
it rather than re-derived (custom code is only the market-information
estimator itself, in ``market_information.py``).
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import gamma


def critical_value(confidence: float, n: int, L: int = 1) -> float:
    """Asymptotic critical value of I_hat^{L+1} at a given confidence level.

    Rejects the null hypothesis (efficient market) when the observed
    I_hat^{L+1} exceeds this value. Gamma(k, theta) with k = 2^(L-1) and
    theta = 1 / (ln(2) * n) (paper, Eq. (11)).

    Parameters
    ----------
    confidence : float
        Confidence level in (0, 1), e.g. 0.95, 0.99, 0.999.
    n : int
        Rolling-window length used to estimate the market information.
    L : int
        Order of the Markov dependence tested (paper's L). Default 1.

    Returns
    -------
    float
        The critical value, i.e. the (confidence) quantile of
        Gamma(2^(L-1), 1/(ln(2)*n)).
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if n <= 0:
        raise ValueError("n must be positive")
    shape = 2 ** (L - 1)
    scale = 1.0 / (np.log(2.0) * n)
    return float(gamma.ppf(confidence, a=shape, scale=scale))


def rejection_table(
    info_series: pd.Series,
    n: int,
    confidence_levels: Iterable[float],
    L: int = 1,
) -> tuple[pd.DataFrame, dict[float, float]]:
    """Per-date EMH rejection decisions at each confidence level.

    Parameters
    ----------
    info_series : pd.Series
        Estimated market information I_hat^{L+1}, indexed by date (output of
        :func:`src.market_information.rolling_market_information`).
    n : int
        Rolling-window length used to estimate ``info_series``.
    confidence_levels : Iterable[float]
        Confidence levels to test at, e.g. (0.95, 0.99, 0.999).
    L : int
        Order of the Markov dependence tested. Default 1.

    Returns
    -------
    table : pd.DataFrame
        Column "I2_hat" plus one boolean column "reject_<level>" per
        confidence level (True where the EMH is rejected at that date).
    thresholds : dict[float, float]
        Confidence level -> critical value used for that column.
    """
    confidence_levels = list(confidence_levels)
    thresholds = {c: critical_value(c, n, L) for c in confidence_levels}
    table = pd.DataFrame({"I2_hat": info_series})
    for c in confidence_levels:
        table[f"reject_{c}"] = table["I2_hat"] > thresholds[c]
    return table, thresholds


def rejection_rates(table: pd.DataFrame, confidence_levels: Iterable[float]) -> dict[float, float]:
    """Percentage of dates at which the EMH is rejected, per confidence level.

    Parameters
    ----------
    table : pd.DataFrame
        Output of :func:`rejection_table`.
    confidence_levels : Iterable[float]
        Confidence levels whose rejection columns are summarised.

    Returns
    -------
    dict[float, float]
        Confidence level -> percentage (0-100) of dates with a rejection.
    """
    if len(table) == 0:
        raise ValueError("empty rejection table")
    rates = {}
    for c in confidence_levels:
        column = f"reject_{c}"
        if column not in table.columns:
            raise KeyError(f"missing column {column!r}; run rejection_table first")
        rates[c] = 100.0 * table[column].mean()
    return rates
