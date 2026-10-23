#!/bin/sh
# Generates five synthetic export shapes (Stripe plus HubSpot, Chargebee, QuickBooks plus a wide Excel schedule, Maxio with resellers, 3,000 customer scale) and runs the kit on each.
cd "$(dirname "$0")"
python3 gen_stress.py --out stress || exit 1
for s in stripe chargebee quickbooks maxio scale; do
  d=stress/$s; sched=$d/schedule.csv; [ -f $d/schedule.xlsx ] && sched=$d/schedule.xlsx
  start=$(date +%s)
  if out=$(python3 pilot.py --schedule $sched --invoices $d/invoices.csv --map $d/mapping.json --asof 2025-10 --out $d/out 2>&1); then
    echo "$s: ok in $(( $(date +%s) - start ))s"
  else
    echo "$s: FAIL $(echo "$out" | grep -E "Error|error" | tail -1)"
  fi
done
