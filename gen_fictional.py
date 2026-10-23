#!/usr/bin/env python3
"""Fictional pilot data for testing the kit. No real company, no real data.

Writes example/inputs/schedule.csv (customer schedule, one row per customer per month,
the shape most CRM or billing exports take) and example/inputs/invoices.csv (invoice lines).

Planted situations, so every exception bucket in pilot.py has at least one case:
  F-001  clean, fully supported
  F-002  CRM over states: schedule 5,000, invoices 4,200 all year
  F-003  credit memo in 2025-06, rebill in 2025-07 (same period billed twice, then credited)
  F-004  timing: billed in arrears on the 1st of the next month, no service period on the lines; schedule steps up in 2025-05
  F-005  ramp: schedule shows 8,000 from day one, invoices 4,000 for the first three months
  F-006  name only match: schedule id blank, name "Acme Corp" vs invoices "ACME Corporation"
  F-007  in schedule, no invoices at all (unmatched, schedule only)
  INV-ONLY-1  invoices for a customer that is not in the schedule
  F-008  untyped one off line beside the subscription (classification, needs review)
  F-009  churned in 2025-08 on the schedule, invoices continue to 2025-10 (under stated)
  F-010  annual prepay: one invoice for 12 months, schedule monthly
  F-011  duplicate invoice id (same line twice)
  F-012  under stated: schedule 1,000, invoices 1,300
"""
import csv, os, random
from datetime import date

random.seed(7)
import sys
OUT = sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "example", "inputs")
os.makedirs(OUT, exist_ok=True)
MONTHS = [date(2024, m, 1) for m in range(10, 13)] + [date(2025, m, 1) for m in range(1, 11)]  # 2024-10 .. 2025-10


def month_end(d):
    nxt = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)
    return date.fromordinal(nxt.toordinal() - 1)


schedule = []  # customer_id, customer_name, snapshot_date, mrr, start_date, end_date, status
invoices = []  # invoice_id, customer_id, customer_name, invoice_date, service_start, service_end, amount, line_type, description
inv_n = [1000]


def inv(cid, cname, d, s, e, amount, line_type="recurring", desc="Subscription", iid=None):
    inv_n[0] += 1
    invoices.append(dict(invoice_id=iid or f"INV-{inv_n[0]}", customer_id=cid, customer_name=cname,
                         invoice_date=d.isoformat(), service_start=s.isoformat() if s else "",
                         service_end=e.isoformat() if e else "", amount=f"{amount:.2f}", line_type=line_type,
                         description=desc))


def sched(cid, cname, mrr, months, start, end=None, status="active"):
    for m in months:
        if end is not None and m > end:
            continue
        schedule.append(dict(customer_id=cid, customer_name=cname, snapshot_date=month_end(m).isoformat(),
                             mrr=f"{mrr:.2f}", start_date=start.isoformat(), end_date=end.isoformat() if end else "",
                             status=status))


# 30 background customers: 24 clean, 4 churn mid window (schedule and invoices agree), 2 downgrade (agree)
for i in range(13, 43):
    cid = f"F-{i:03d}"; name = f"Fictional Co {i}"; mrr = random.choice([500, 900, 1500, 2200, 3100, 4000])
    if i in (15, 22, 31, 40):
        end = date(2025, 3 + (i % 4), 1)
        sched(cid, name, mrr, MONTHS, date(2024, 3, 1), end=end)
        for m in MONTHS:
            if m <= end: inv(cid, name, m, m, month_end(m), mrr)
    elif i in (18, 27):
        for m in MONTHS:
            v = mrr if m < date(2025, 6, 1) else mrr * 0.6
            sched(cid, name, v, [m], date(2024, 3, 1))
            inv(cid, name, m, m, month_end(m), v)
    else:
        sched(cid, name, mrr, MONTHS, date(2024, 3, 1))
        for m in MONTHS:
            inv(cid, name, m, m, month_end(m), mrr)

# F-001 clean
sched("F-001", "Blue Harbor Analytics", 2500, MONTHS, date(2024, 1, 15))
for m in MONTHS: inv("F-001", "Blue Harbor Analytics", m, m, month_end(m), 2500)

# F-002 CRM over states
sched("F-002", "Granite Peak Software", 5000, MONTHS, date(2023, 11, 1))
for m in MONTHS: inv("F-002", "Granite Peak Software", m, m, month_end(m), 4200)

# F-003 credit memo and rebill
sched("F-003", "Cedar Loop Systems", 3000, MONTHS, date(2024, 2, 1))
for m in MONTHS:
    inv("F-003", "Cedar Loop Systems", m, m, month_end(m), 3000)
    if m == date(2025, 6, 1):
        inv("F-003", "Cedar Loop Systems", date(2025, 6, 20), m, month_end(m), -3000, "credit", "Credit memo, billing error")
        inv("F-003", "Cedar Loop Systems", date(2025, 7, 2), m, month_end(m), 3000, "recurring", "Rebill June")

# F-004 timing: billed in arrears on the 1st of the next month with no service period; schedule steps up in 2025-05
for m in MONTHS:
    sched("F-004", "Northwind Dynamics", 1800 if m < date(2025, 5, 1) else 2400, [m], date(2024, 6, 1))
    nxt = date(m.year + (m.month == 12), (m.month % 12) + 1, 1)
    inv("F-004", "Northwind Dynamics", nxt, None, None, 1800 if m < date(2025, 5, 1) else 2400, desc=f"Subscription {m.strftime('%B %Y')}")

# F-005 ramp
sched("F-005", "Juniper Ridge Labs", 8000, MONTHS[3:], date(2025, 1, 1))
for k, m in enumerate(MONTHS[3:]):
    inv("F-005", "Juniper Ridge Labs", m, m, month_end(m), 4000 if k < 3 else 8000)

# F-006 name only match
for m in MONTHS:
    schedule.append(dict(customer_id="", customer_name="Acme Corp", snapshot_date=month_end(m).isoformat(), mrr="1200.00",
                         start_date="2024-05-01", end_date="", status="active"))
for m in MONTHS: inv("", "ACME Corporation", m, m, month_end(m), 1200)

# F-007 schedule only
sched("F-007", "Silent Partner Inc", 2100, MONTHS, date(2024, 8, 1))

# INV-ONLY-1 invoices only
for m in MONTHS[4:]: inv("INV-ONLY-1", "Orphan Billing LLC", m, m, month_end(m), 950)

# F-008 non recurring services
sched("F-008", "Maple Street Health", 2600, MONTHS, date(2024, 4, 1))
for m in MONTHS: inv("F-008", "Maple Street Health", m, m, month_end(m), 2600)
inv("F-008", "Maple Street Health", date(2025, 3, 10), None, None, 15000, "", "Implementation")

# F-009 churned on schedule, invoices continue
sched("F-009", "Lantern Field Co", 1400, MONTHS, date(2024, 1, 1), end=date(2025, 8, 1))
for m in MONTHS: inv("F-009", "Lantern Field Co", m, m, month_end(m), 1400)

# F-010 annual prepay
sched("F-010", "Copperline Freight", 2000, MONTHS, date(2024, 11, 1))
inv("F-010", "Copperline Freight", date(2024, 11, 1), date(2024, 11, 1), date(2025, 10, 31), 24000, desc="Annual subscription")

# F-011 duplicate invoice id
sched("F-011", "Harbor Light Media", 1700, MONTHS, date(2024, 9, 1))
for m in MONTHS:
    iid = f"DUP-{m.strftime('%Y%m')}"
    inv("F-011", "Harbor Light Media", m, m, month_end(m), 1700, iid=iid)
    if m == date(2025, 4, 1): inv("F-011", "Harbor Light Media", m, m, month_end(m), 1700, iid=iid)

# F-012 under stated
sched("F-012", "Quiet Creek Software", 1000, MONTHS, date(2024, 7, 1))
for m in MONTHS: inv("F-012", "Quiet Creek Software", m, m, month_end(m), 1300)

random.shuffle(invoices)
with open(os.path.join(OUT, "schedule.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(schedule[0].keys())); w.writeheader(); w.writerows(schedule)
with open(os.path.join(OUT, "invoices.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(invoices[0].keys())); w.writeheader(); w.writerows(invoices)
print(f"wrote {len(schedule)} schedule rows and {len(invoices)} invoice lines to {OUT}")
