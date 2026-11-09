"""Estimator of the market information and its rolling computation.

Custom implementation of the market-information estimator of Section 3.1 of
the paper (no library implements this entropy-based market-efficiency
statistic), specialised to the order L = 1 used in the empirical study of
Section 4.

Notation follows the paper: a daily price series P_0, ..., P_T is converted
into a binary return series X_1, ..., X_T with X_i = 1{P_i - P_{i-1} > 0}
(zero and negative returns both give X_i = 0, since the paper's indicator is
strictly "> 0"). For L = 1 there are 2^L = 2 possible length-1 prefixes,
G_1 = (0) and G_2 = (1). For a window of n consecutive binary returns
X_t, ..., X_{t+n-1}:

    n_i = number of times prefix G_i occurs among X_t, ..., X_{t+n-2}
    j_i = number of times X_{t+k+1} = 1 follows an occurrence of G_i
    p_hat_i = n_i / (n - 1)
    pi_hat_i = j_i / n_i

    I_hat^2 = sum_i [ -p_hat_i * log2(p_hat_i / 2)
                       + p_hat_i * pi_hat_i * log2(p_hat_i * pi_hat_i)
                       + p_hat_i * (1 - pi_hat_i) * log2(p_hat_i * (1 - pi_hat_i)) ]

with the convention 0 * log2(0) = 0. Algebraically (used here for a numerically
simpler and equivalent computation) this reduces to

    I_hat^2 = 1 - sum_i p_hat_i * h(pi_hat_i)

where h(p) = -p*log2(p) - (1-p)*log2(1-p) is the binary (Shannon) entropy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def binary_returns(prices: pd.Series) -> pd.Series:
    """Convert a price series into the binary return series X_i.

    X_i = 1{P_i - P_{i-1} > 0}, so unchanged or falling prices give X_i = 0
    (paper, Section 2). The first price has no predecessor and is dropped.

    Parameters
    ----------
    prices : pd.Series
        Daily price series indexed by date, sorted ascending in time.

    Returns
    -------
    pd.Series of int (0/1), indexed like ``prices`` from the second date on.
    """
    if prices.isna().any():
        raise ValueError("price series contains missing values")
    diffs = prices.diff().iloc[1:]
    return (diffs > 0).astype(int)


def _binary_entropy(p: float) -> float:
    """Binary (Shannon) entropy h(p) in bits, with 0 * log2(0) := 0."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * np.log2(p) - (1.0 - p) * np.log2(1.0 - p)


def market_information_order1(x: np.ndarray) -> float:
    """Estimated market information I_hat^2 for L = 1 on one window.

    Parameters
    ----------
    x : np.ndarray
        A 1-D array of n binary returns (0/1), n >= 2.

    Returns
    -------
    float
        The estimated market information I_hat^2 >= 0 (paper, Eq. (1)-(2)
        specialised to L = 1).
    """
    x = np.asarray(x)
    n = x.shape[0]
    if n < 2:
        raise ValueError("a window of at least 2 binary returns is required")
    if not np.isin(x, (0, 1)).all():
        raise ValueError("binary returns must be 0 or 1")

    prefix = x[:-1]
    suffix = x[1:]
    total = n - 1  # number of (prefix, suffix) pairs, i.e. n_0 + n_1

    weighted_entropy = 0.0
    for prefix_value in (0, 1):
        mask = prefix == prefix_value
        n_i = int(mask.sum())
        if n_i == 0:
            continue  # p_hat_i = 0, so this prefix contributes 0 regardless
        j_i = int(suffix[mask].sum())
        p_hat_i = n_i / total
        pi_hat_i = j_i / n_i
        weighted_entropy += p_hat_i * _binary_entropy(pi_hat_i)

    info = 1.0 - weighted_entropy
    assert info >= -1e-9, "market information must be non-negative"
    return max(info, 0.0)


def rolling_market_information(returns: pd.Series, window: int) -> pd.Series:
    """Rolling I_hat^2 (L = 1) over consecutive non-overlapping-free windows.

    At each date t (the last observation of a window), the window uses the
    ``window`` most recent binary returns up to and including t, so no future
    observation enters the estimate at date t (paper, Section 4: a rolling
    window of n = 100 business days).

    Parameters
    ----------
    returns : pd.Series
        Binary return series (0/1), as produced by :func:`binary_returns`.
    window : int
        Window length n (paper: n = 100).

    Returns
    -------
    pd.Series
        I_hat^2 indexed by the date of the last observation of each window.
    """
    if window < 2:
        raise ValueError("window must be at least 2")
    values = returns.to_numpy()
    index = returns.index
    if len(values) < window:
        return pd.Series(dtype=float)

    estimates = {}
    for end in range(window - 1, len(values)):
        start = end - window + 1
        estimates[index[end]] = market_information_order1(values[start:end + 1])
    return pd.Series(estimates, name="I2_hat")
