#!/bin/sh
# Regenerates the fictional Larkspur data and runs the kit on it. Touches only example/.
set -e
cd "$(dirname "$0")"
python3 gen_fictional.py --out example/inputs
rm -rf example/outputs 2>/dev/null || true
python3 pilot.py --schedule example/inputs/schedule.csv --invoices example/inputs/invoices.csv --map example/inputs/mapping.json --asof 2025-10 --out example/outputs

# The fictional general ledger, derived from the kit's own roll forward and then
# moved by one account.
#
# WHY IT IS DERIVED AND NOT WRITTEN BY gen_fictional.py. The implied balance
# depends on how the kit spreads an annual prepay, and the fictional set plants
# one. A generator that worked the balance out for itself would be a second
# allocation path beside the kit's, and the first version of this got a flat
# 800 a month because it assumed every line recognises in the month it bills.
# So the GL is the kit's figure plus exactly 800 a month, which is Granite Peak
# Software: the schedule carries it at 5,000 where the invoices support 4,200,
# and a company that kept its deferred balance on the schedule basis for that
# one account would sit exactly that far above the invoices. The difference
# column then reads -800 in every month, and a reader who follows it finds the
# same account the exceptions table already names.
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("example/outputs/deferred_rollforward.csv")))
with open("example/inputs/deferred_gl.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["month", "balance"]); w.writeheader()
    for r in rows:
        w.writerow({"month": r["month"], "balance": f'{float(r["closing"]) + 800.0:.2f}'})
print(f"wrote example/inputs/deferred_gl.csv, {len(rows)} months, Granite Peak planted at 800 a month")
PY

python3 pilot.py --schedule example/inputs/schedule.csv --invoices example/inputs/invoices.csv --map example/inputs/mapping.json --asof 2025-10 --out example/outputs --deferred-gl example/inputs/deferred_gl.csv
echo
echo "Expected: ten accounts under Accounts to review first in example/outputs/report.md. The other two planted cases are the name only match (match_table.csv, normalised_name) and the annual prepay (supported)."
