#!/usr/bin/env python3
"""The Larkspur set one month later, for the month over month diff. Fictional.

Reads example/inputs/schedule.csv and invoices.csv (as of 2025-10) and writes
example/next_month/schedule.csv and invoices.csv (as of 2025-11): every account that
carried MRR or billing in October carries the same in November, except four planted changes.

Planted, against the October run:
  resolved  Harbor Light Media   the duplicate invoice DUP-202504 is removed from the export
  resolved  Maple Street Health  the untyped 15,000 line in March 2025 is now typed "services"
  changed   Granite Peak Software  the schedule is corrected to 4,200 for November (unresolved MRR 800 to 0; eleven months still over stated)
  new       Nimbus Field Systems  a customer billed in November that is not on the schedule
  (and the Copperline annual prepay renews on 1 Nov on the same terms, so it stays supported)
Expected from diff_runs.py: new 1, resolved 2, changed 1. Written to example/next_month/expected.json.
"""
import csv, json, os, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "example", "inputs")
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "example", "next_month")
os.makedirs(OUT, exist_ok=True)

sched = list(csv.DictReader(open(os.path.join(SRC, "schedule.csv"))))
inv = list(csv.DictReader(open(os.path.join(SRC, "invoices.csv"))))

# November schedule rows: copy October's
nov = []
for r in sched:
    if r["snapshot_date"].startswith("2025-10"):
        n = dict(r); n["snapshot_date"] = "2025-11-30"
        if r["customer_name"] == "Granite Peak Software":
            n["mrr"] = "4200.00"
        nov.append(n)
sched_out = sched + nov

# November invoices: copy October's recurring lines with November dates, drop the duplicate, type the one off
inv_out = []
seen_dup = False
for r in inv:
    if r["invoice_id"] == "DUP-202504":
        if seen_dup:
            continue
        seen_dup = True
    if r["customer_name"] == "Maple Street Health" and r["line_type"].strip() == "" and r["amount"].startswith("15000"):
        r = dict(r); r["line_type"] = "services"
    inv_out.append(r)
n = max(int(r["invoice_id"].split("-")[1]) for r in inv if r["invoice_id"].startswith("INV-") and r["invoice_id"].split("-")[1].isdigit())
for r in inv:
    if r["invoice_date"].startswith("2025-10") and r["line_type"] == "recurring":
        n += 1
        m = dict(r); m["invoice_id"] = f"INV-{n}"
        m["invoice_date"] = r["invoice_date"].replace("2025-10", "2025-11")
        m["service_start"] = r["service_start"].replace("2025-10", "2025-11") if r["service_start"] else ""
        m["service_end"] = "2025-11-30" if r["service_end"] else ""
        inv_out.append(m)
# the annual prepay (F-010) ran to 2025-10-31; it renews on the same terms, otherwise November would read as over stated
n += 1
inv_out.append(dict(invoice_id=f"INV-{n}", customer_id="F-010", customer_name="Copperline Freight", invoice_date="2025-11-01",
                    service_start="2025-11-01", service_end="2026-10-31", amount="24000.00", line_type="recurring", description="Annual subscription, renewal"))
n += 1
inv_out.append(dict(invoice_id=f"INV-{n}", customer_id="F-099", customer_name="Nimbus Field Systems", invoice_date="2025-11-01",
                    service_start="2025-11-01", service_end="2025-11-30", amount="2100.00", line_type="recurring", description="Subscription"))

with open(os.path.join(OUT, "schedule.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched_out)
with open(os.path.join(OUT, "invoices.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(inv[0])); w.writeheader(); w.writerows(inv_out)
json.dump({"asof": "2025-11", "new": ["Nimbus Field Systems"], "resolved": ["Harbor Light Media", "Maple Street Health"], "changed": ["Granite Peak Software"]},
          open(os.path.join(OUT, "expected.json"), "w"), indent=2)
print(f"wrote {len(sched_out)} schedule rows and {len(inv_out)} invoice lines to {OUT}; expected new 1, resolved 2, changed 1")
