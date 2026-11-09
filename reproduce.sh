#!/usr/bin/env bash
# Runs the test suite and the paper's empirical-application experiment
# (Section 4 of the paper) with the same commands as README.md.
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "=== Unit tests (no network/credentials required) ==="
python -m pytest -m "not market_data"

echo "=== Full test suite (requires DATALOADER_API_KEY/MASSIVE_API_KEY) ==="
python -m pytest

echo "=== Experiment 4: empirical application to real financial time series ==="
python -m exp.exp4
