#!/bin/sh
# Regenerates the fictional Larkspur data and runs the kit on it. Touches only example/.
set -e
cd "$(dirname "$0")"
python3 gen_fictional.py --out example/inputs
rm -rf example/outputs 2>/dev/null || true
python3 pilot.py --schedule example/inputs/schedule.csv --invoices example/inputs/invoices.csv --map example/inputs/mapping.json --asof 2025-10 --out example/outputs
echo
echo "Expected: ten accounts under Accounts to review first in example/outputs/report.md. The other two planted cases are the name only match (match_table.csv, normalised_name) and the annual prepay (supported)."
