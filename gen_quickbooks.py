#!/usr/bin/env python3
"""A fictional QuickBooks Online shaped pair with a known deferred revenue answer.

QuickBooks Online invoice exports carry no service period. This writes example/quickbooks/
schedule.csv (one row per customer per month), invoices.csv (QuickBooks columns: Date,
Transaction Type, Num, Customer, Memo/Description, Amount) and mapping.json.

Planted, and the deferred revenue closing balance at 2025-10 they imply:
  five monthly customers .................................... 0 deferred
  Annual One, 2,000 a month, 24,000 billed 15 Jan 2025 ....... 4,000 (two months left)
  Annual Two, 1,500 a month, 18,000 billed 1 Jun 2025 ........ 10,500 (seven months left)
  Annual Three, 3,000 a month, 36,000 billed Oct 2024 and Oct 2025 ... 33,000 (eleven left)
  Quarterly One, 900 a month, 2,700 billed each Jan, Apr, Jul, Oct .. 1,800 (two left)
  Discount Co, 1,000 a month, 10,800 billed Mar 2025 (10 percent off an annual)
      not an exact multiple of the schedule, so NOT given a period: stays in March, flagged
  Total expected deferred at 2025-10: 49,300.
"""
import csv, json, os, sys
from datetime import date

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "example", "quickbooks")
os.makedirs(OUT, exist_ok=True)
MONTHS = [date(2024 + (m - 1) // 12, (m - 1) % 12 + 1, 1) for m in range(1, 23)]  # 2024-01 .. 2025-10

customers = [("Monthly A", 500), ("Monthly B", 800), ("Monthly C", 1000), ("Monthly D", 1200), ("Monthly E", 600),
             ("Annual One", 2000), ("Annual Two", 1500), ("Annual Three", 3000), ("Quarterly One", 900), ("Discount Co", 1000)]
start = {"Annual Two": date(2025, 6, 1)}
sched, inv = [], []
num = 1000

def add(d, name, amount, kind="Invoice", memo="Subscription"):
    global num
    num += 1
    inv.append({"Date": d.strftime("%m/%d/%Y"), "Transaction Type": kind, "Num": str(num), "Customer": name, "Memo/Description": memo, "Amount": f"{amount:,.2f}"})

for name, mrr in customers:
    for m in MONTHS:
        if m < start.get(name, date(2024, 1, 1)):
            continue
        sched.append({"customer_name": name, "snapshot_date": m.isoformat(), "mrr": f"{mrr:.2f}"})
        if name.startswith("Monthly"):
            add(m, name, mrr)
        elif name == "Quarterly One" and m.month in (1, 4, 7, 10):
            add(m, name, 3 * mrr, memo="Quarterly subscription")
    if name == "Annual One":
        add(date(2024, 1, 15), name, 12 * mrr, memo="Annual subscription"); add(date(2025, 1, 15), name, 12 * mrr, memo="Annual subscription")
    if name == "Annual Two":
        add(date(2025, 6, 1), name, 12 * mrr, memo="Annual subscription")
    if name == "Annual Three":
        add(date(2023, 10, 10), name, 12 * mrr, memo="Annual subscription"); add(date(2024, 10, 10), name, 12 * mrr, memo="Annual subscription"); add(date(2025, 10, 10), name, 12 * mrr, memo="Annual subscription")
    if name == "Discount Co":
        add(date(2024, 3, 5), name, 10.8 * mrr, memo="Annual subscription, 10 percent off"); add(date(2025, 3, 5), name, 10.8 * mrr, memo="Annual subscription, 10 percent off")

with open(os.path.join(OUT, "schedule.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
with open(os.path.join(OUT, "invoices.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(inv[0])); w.writeheader(); w.writerows(inv)
mapping = {
    "schedule": {"format": "snapshot", "customer_id": "", "customer_name": "customer_name", "snapshot_date": "snapshot_date", "mrr": "mrr", "arr": "", "start_date": "", "end_date": "", "status": ""},
    "invoices": {"invoice_id": "Num", "customer_id": "", "customer_name": "Customer", "invoice_date": "Date", "service_start": "", "service_end": "", "amount": "Amount", "line_type": "Transaction Type", "description": "Memo/Description"},
    "rules": {"recurring_types": ["invoice"], "credit_types": ["credit memo"], "non_recurring_types": [], "tolerance_pct": 1.0, "tolerance_abs": 5.0, "ramp_months": 3, "months_for_retention": 12,
              "periodless_recurring": "whole_months_from_schedule"},
}
json.dump(mapping, open(os.path.join(OUT, "mapping.json"), "w"), indent=2)
print(f"wrote {len(sched)} schedule rows and {len(inv)} invoice lines to {OUT}; expected deferred at 2025-10: 49,300")
