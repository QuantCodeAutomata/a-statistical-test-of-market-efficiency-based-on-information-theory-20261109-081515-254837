"""Experiment 4: empirical application of the market-efficiency test.

Reproduces the empirical study of Section 4 of the paper: the market
information I_hat^2 (L = 1) is estimated in a rolling window of n = 100
business days (calendar days for BTC/USD) for four series of daily prices in
2021 - the CAC 40 index, the Russell 2000 index, the Perficient stock, and
the BTC/USD cryptocurrency pair - and the statistical test of market
efficiency (Section 3.3) is applied at each date at the 95%, 99%, and 99.9%
confidence levels (Figure 6 and its discussion, Section 4).

Usage
-----
    python -m exp.exp4
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data.data_loader import load_price_panel
from src import config
from src.efficiency_test import rejection_rates, rejection_table
from src.market_information import binary_returns, rolling_market_information

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def run() -> dict:
    """Run Experiment 4 end to end and save tables, plots, and metrics."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    prices, load_meta = load_price_panel(
        config.TICKERS,
        config.START_DATE,
        config.END_DATE,
        identity_date=config.IDENTITY_DATE,
        adjust_dividends=config.ADJUST_DIVIDENDS,
        price_field=config.PRICE_FIELD,
        equity_names=config.EQUITY_SERIES,
        crypto_names=config.CRYPTO_SERIES,
    )

    log = {"load_metadata": load_meta}
    print("Loaded price panel:")
    for name, info in load_meta.items():
        print(f"  {name}: {info}")

    summary_rows = []
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=False)
    axes = axes.ravel()

    tables: dict[str, pd.DataFrame] = {}
    thresholds_ref = None
    for ax, (name, price_series) in zip(axes, prices.items()):
        returns = binary_returns(price_series)
        info_series = rolling_market_information(returns, config.WINDOW_N)
        if info_series.empty:
            raise ValueError(f"{name}: not enough observations for a window of {config.WINDOW_N}")

        table, thresholds = rejection_table(
            info_series, config.WINDOW_N, config.CONFIDENCE_LEVELS, L=config.L_ORDER
        )
        thresholds_ref = thresholds
        rates = rejection_rates(table, config.CONFIDENCE_LEVELS)
        tables[name] = table

        summary_rows.append({
            "asset": name,
            "n_dates": len(table),
            "first_date": str(table.index.min().date()),
            "last_date": str(table.index.max().date()),
            "mean_I2_hat": float(table["I2_hat"].mean()),
            **{f"pct_reject_{c}": rates[c] for c in config.CONFIDENCE_LEVELS},
        })

        ax.plot(table.index, table["I2_hat"], label=r"$\widehat{I}^2$", color="tab:blue")
        colors = {0.95: "tab:green", 0.99: "tab:orange", 0.999: "tab:red"}
        for c in config.CONFIDENCE_LEVELS:
            ax.axhline(thresholds[c], linestyle="--", color=colors.get(c, "grey"),
                       label=f"{c * 100:.1f}% threshold")
        ax.set_title(name)
        ax.set_xlabel("date")
        ax.set_ylabel(r"$\widehat{I}^2$")
        ax.legend(fontsize=7)

    fig.suptitle(
        r"Estimated market information $\widehat{I}^2$ (L=1, n=100) "
        "and EMH rejection thresholds, 2021"
    )
    fig.tight_layout()
    fig_path = RESULTS_DIR / "exp4_market_information.png"
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    summary = pd.DataFrame(summary_rows).set_index("asset")
    summary_path = RESULTS_DIR / "exp4_summary.csv"
    summary.to_csv(summary_path)

    for name, table in tables.items():
        safe_name = name.replace("/", "").replace(" ", "_")
        table.to_csv(RESULTS_DIR / f"exp4_series_{safe_name}.csv")

    log["thresholds"] = thresholds_ref
    log["summary"] = summary.reset_index().to_dict(orient="records")
    log_path = RESULTS_DIR / "exp4_log.json"
    log_path.write_text(json.dumps(log, indent=2, default=str))

    print("\nSummary (percentage of dates with EMH rejection):")
    print(summary)
    print(f"\nSaved: {fig_path}, {summary_path}, {log_path}")
    return {"summary": summary, "tables": tables, "thresholds": thresholds_ref, "log": log}


if __name__ == "__main__":
    run()
