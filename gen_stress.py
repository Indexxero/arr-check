#!/usr/bin/env python3
"""Stress shapes for the kit. One fictional company written in five real export layouts, with mess planted.

Writes stress/<shape>/schedule.* , invoices.* and mapping.json for:
  stripe      Stripe invoice line export (UTC timestamps, two currencies, credit notes, usage lines) + HubSpot deal export as the schedule (contract format, ARR not MRR, US dates)
  chargebee   Chargebee invoices (dd-Mon-yyyy, credits applied column) + Chargebee subscription snapshot (MRR, mid month starts, churn and return)
  quickbooks  QuickBooks invoice list (no service period, Credit Memo rows, mm/dd/yyyy) + hand kept wide Excel schedule (one column per month, .xlsx)
  maxio       Maxio style monthly subscription snapshot with parent customer (reseller) + invoices with several lines per month and a mid term price change
  scale       3,000 customers, 24 months, tidy format, for timing only

No real company. Seeded.
"""
import csv, json, os, random
from datetime import date, timedelta
import pandas as pd

random.seed(11)
import sys
BASE = sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "stress")
MONTHS = [date(2024, m, 1) for m in range(10, 13)] + [date(2025, m, 1) for m in range(1, 11)]


def mend(d):
    n = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)
    return date.fromordinal(n.toordinal() - 1)


def write(shape, sched_rows, sched_cols, inv_rows, inv_cols, mapping, sched_xlsx=False):
    d = os.path.join(BASE, shape); os.makedirs(d, exist_ok=True)
    if sched_xlsx:
        pd.DataFrame(sched_rows, columns=sched_cols).to_excel(os.path.join(d, "schedule.xlsx"), index=False)
    else:
        with open(os.path.join(d, "schedule.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=sched_cols); w.writeheader(); w.writerows(sched_rows)
    with open(os.path.join(d, "invoices.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_cols); w.writeheader(); w.writerows(inv_rows)
    json.dump(mapping, open(os.path.join(d, "mapping.json"), "w"), indent=2)
    print(shape, len(sched_rows), "schedule rows,", len(inv_rows), "invoice lines")


RULES = {"recurring_types": ["recurring", "subscription", "license", "saas", "plan", "invoice"], "credit_types": ["credit", "credit memo", "credit note", "refund", "adjustment"],
         "non_recurring_types": ["services", "setup", "implementation", "one time", "onboarding", "usage", "overage", "hardware", "metered"],
         "tolerance_pct": 1.0, "tolerance_abs": 5.0, "ramp_months": 3, "months_for_retention": 12}

# ---------- 1 stripe + hubspot ----------
def stripe():
    names = [("cus_A1", "Blue Harbor Analytics", 2500), ("cus_A2", "Granite Peak Software", 5000), ("cus_A3", "Cedar Loop Systems", 3000), ("cus_A4", "Maple Street Health", 2600),
             ("cus_A5", "Juniper Ridge Labs", 8000), ("cus_A6", "Acme Corp", 1200), ("cus_A7", "Quiet Creek Software", 1000), ("cus_A8", "Harbor Light Media", 1700),
             ("cus_A9", "Lantern Field Co", 1400), ("cus_B1", "Nordlicht GmbH", 2000)] + [(f"cus_C{i}", f"Fictional Co {i}", random.choice([500, 900, 1500, 2200])) for i in range(10, 40)]
    inv, sched = [], []
    n = 5000
    for cid, name, mrr in names:
        cur = "eur" if cid == "cus_B1" else "usd"
        # HubSpot deal export as the schedule: contract format, ARR, US dates, typos in two names
        hs_name = name.replace("Harbor", "Harbour") if cid == "cus_A1" else (name + " Inc." if cid == "cus_A3" else name)
        start = date(2024, 6, 15) if cid == "cus_A5" else date(2024, 3, 1)
        end = "" if cid != "cus_A9" else "08/31/2025"
        sched.append({"Record ID": cid.replace("cus_", "") if cid != "cus_A6" else "", "Deal Name": f"{hs_name} renewal", "Company name": hs_name, "Amount": f"{mrr*12:,.2f}", "Annual Recurring Revenue": f"${mrr*12:,.2f}",
                      "Contract Start Date": start.strftime("%m/%d/%Y"), "Contract End Date": end, "Deal Stage": "Closed Won", "Currency": cur.upper()})
        if cid == "cus_A2":  # duplicate schedule row
            sched.append(dict(sched[-1]))
        for m in MONTHS:
            if cid == "cus_A9" and m > date(2025, 8, 1):
                continue
            amt = mrr
            if cid == "cus_A5" and m < date(2025, 1, 1):
                continue
            if cid == "cus_A4" and m >= date(2025, 6, 1):
                amt = 3100  # mid term price change on invoices only
            n += 1
            ps = m if not (cid == "cus_A5" and m == date(2024, 6, 1)) else date(2024, 6, 15)
            inv.append({"Invoice ID": f"in_{n}", "Customer ID": cid, "Customer Name": name, "Customer Email": f"ap@{name.split()[0].lower()}.example", "Created (UTC)": f"{m.isoformat()} 14:0{n%10}",
                        "Period Start (UTC)": f"{ps.isoformat()} 00:00", "Period End (UTC)": f"{mend(m).isoformat()} 23:59", "Amount": f"{amt:,.2f}", "Currency": cur, "Status": "paid", "Description": "Platform subscription", "Line Item Type": "subscription"})
            if cid == "cus_A3" and m == date(2025, 6, 1):
                inv.append({**inv[-1], "Invoice ID": f"cn_{n}", "Amount": f"-{amt:,.2f}", "Description": "Credit note, billing error", "Line Item Type": "credit_note"})
                inv.append({**inv[-1], "Invoice ID": f"in_{n}r", "Amount": f"{amt:,.2f}", "Description": "Rebill June", "Line Item Type": "subscription"})
            if cid == "cus_A7":  # usage line every month plus a partial refund once
                inv.append({**inv[-1], "Invoice ID": f"in_{n}u", "Period Start (UTC)": "", "Period End (UTC)": "", "Amount": f"{random.choice([120, 340, 90]):,.2f}", "Description": "Metered API usage", "Line Item Type": "metered"})
                if m == date(2025, 3, 1):
                    inv.append({**inv[-1], "Invoice ID": f"re_{n}", "Amount": "-200.00", "Description": "Partial refund", "Line Item Type": "refund"})
            if cid == "cus_A8" and m == date(2025, 4, 1):
                inv.append(dict(inv[-1]))  # exact duplicate row
    random.shuffle(inv)
    mapping = {"schedule": {"format": "contract", "customer_id": "Record ID", "customer_name": "Company name", "snapshot_date": "", "mrr": "", "arr": "Annual Recurring Revenue", "start_date": "Contract Start Date", "end_date": "Contract End Date", "status": "Deal Stage", "currency": "Currency"},
               "invoices": {"invoice_id": "Invoice ID", "customer_id": "Customer ID", "customer_name": "Customer Name", "invoice_date": "Created (UTC)", "service_start": "Period Start (UTC)", "service_end": "Period End (UTC)", "amount": "Amount", "line_type": "Line Item Type", "description": "Description", "currency": "Currency"},
               "rules": {**RULES, "recurring_types": RULES["recurring_types"] + ["subscription"], "credit_types": RULES["credit_types"] + ["credit_note"]}}
    write("stripe", sched, list(sched[0].keys()), inv, list(inv[0].keys()), mapping)


# ---------- 2 chargebee ----------
def chargebee():
    names = [(f"CB{i:03d}", f"Fictional Co {i}", random.choice([450, 990, 1490, 2990])) for i in range(1, 36)]
    inv, sched = [], []
    for cid, name, mrr in names:
        start = date(2024, 3, random.choice([1, 12, 20]))
        churn = date(2025, 4, 1) if cid == "CB005" else None
        back = date(2025, 8, 1) if cid == "CB005" else None  # churn and return
        for m in MONTHS:
            active = (churn is None) or (m < churn) or (back and m >= back)
            if active:
                if not (cid == "CB009" and m == date(2025, 2, 1)):  # blank month on the schedule only
                        sched.append({"Customer Id": cid, "Customer Name": name, "Plan": "Growth", "MRR": f"{mrr:.2f}", "Status": "active", "Snapshot": f"{mend(m).day:02d}-{m.strftime('%b-%Y')}", "Subscription Start": f"{start.day:02d}-{start.strftime('%b-%Y')}"})
                inv.append({"Invoice Number": f"INV-{cid}-{m.strftime('%y%m')}", "Customer Id": cid, "Customer Name": name, "Invoice Date": f"{m.day:02d}-{m.strftime('%b-%Y')}", "Service Period Start": f"{m.day:02d}-{m.strftime('%b-%Y')}", "Service Period End": f"{mend(m).day:02d}-{mend(m).strftime('%b-%Y')}",
                            "Total": f"{mrr:.2f}", "Credits Applied": "0.00", "Plan": "Growth", "Line Type": "Subscription"})
                if cid == "CB012" and m == date(2025, 5, 1):
                    inv[-1]["Credits Applied"] = f"{mrr/2:.2f}"  # credit applied inside the invoice row, no separate line
    mapping = {"schedule": {"format": "snapshot", "customer_id": "Customer Id", "customer_name": "Customer Name", "snapshot_date": "Snapshot", "mrr": "MRR", "arr": "", "start_date": "Subscription Start", "end_date": "", "status": "Status"},
               "invoices": {"invoice_id": "Invoice Number", "customer_id": "Customer Id", "customer_name": "Customer Name", "invoice_date": "Invoice Date", "service_start": "Service Period Start", "service_end": "Service Period End", "amount": "Total", "line_type": "Line Type", "description": "Plan", "credit_amount": "Credits Applied"},
               "rules": RULES}
    write("chargebee", sched, list(sched[0].keys()), inv, list(inv[0].keys()), mapping)


# ---------- 3 quickbooks + wide excel ----------
def quickbooks():
    names = [(f"Fictional Co {i}", random.choice([600, 1200, 2400])) for i in range(1, 31)]
    inv, wide = [], []
    cols = ["Customer"] + [m.strftime("%b-%y") for m in MONTHS]
    for name, mrr in names:
        row = {"Customer": name if name != "Fictional Co 3" else "Fictional Co. 3 (parent)"}
        for m in MONTHS:
            row[m.strftime("%b-%y")] = f"{mrr:,.2f}"
            inv.append({"Date": m.strftime("%m/%d/%Y"), "Transaction Type": "Invoice", "Num": f"{1000 + len(inv)}", "Customer": name, "Memo/Description": "Monthly subscription", "Amount": f"{mrr:,.2f}", "Open Balance": "0.00"})
            if name == "Fictional Co 7" and m == date(2025, 3, 1):
                inv.append({**inv[-1], "Transaction Type": "Credit Memo", "Num": "CM-7", "Amount": f"-{mrr:,.2f}", "Memo/Description": "Credit memo"})
        wide.append(row)
    mapping = {"schedule": {"format": "wide", "customer_id": "", "customer_name": "Customer", "month_columns": "auto", "mrr": "", "arr": "", "snapshot_date": "", "start_date": "", "end_date": "", "status": ""},
               "invoices": {"invoice_id": "Num", "customer_id": "", "customer_name": "Customer", "invoice_date": "Date", "service_start": "", "service_end": "", "amount": "Amount", "line_type": "Transaction Type", "description": "Memo/Description"},
               "rules": RULES}
    write("quickbooks", wide, cols, inv, list(inv[0].keys()), mapping, sched_xlsx=True)


# ---------- 4 maxio with resellers ----------
def maxio():
    inv, sched = [], []
    for i in range(1, 26):
        cid = f"M{i:03d}"; name = f"Fictional Co {i}"; mrr = random.choice([800, 1600, 3200])
        parent = "M001" if i in (2, 3) else ""
        for k, m in enumerate(MONTHS):
            amt = mrr if not (i == 4 and m >= date(2025, 4, 1)) else mrr * 1.25  # mid term price change on both sides
            sched.append({"Customer": name, "Subscription ID": cid, "Parent Customer": parent, "Month": m.strftime("%Y-%m"), "MRR": f"{amt:.2f}", "Status": "Active"})
            for part in (1, 2) if i == 6 else (1,):  # two invoices a month for one customer
                inv.append({"Invoice": f"{cid}-{m.strftime('%Y%m')}-{part}", "Subscription ID": cid, "Customer": name, "Issued": m.isoformat(), "From": m.isoformat(), "To": mend(m).isoformat(), "Amount": f"{amt/(2 if i == 6 else 1):.2f}", "Type": "Recurring"})
    mapping = {"schedule": {"format": "snapshot", "customer_id": "Subscription ID", "customer_name": "Customer", "snapshot_date": "Month", "mrr": "MRR", "arr": "", "start_date": "", "end_date": "", "status": "Status", "parent_id": "Parent Customer"},
               "invoices": {"invoice_id": "Invoice", "customer_id": "Subscription ID", "customer_name": "Customer", "invoice_date": "Issued", "service_start": "From", "service_end": "To", "amount": "Amount", "line_type": "Type", "description": ""},
               "rules": RULES}
    write("maxio", sched, list(sched[0].keys()), inv, list(inv[0].keys()), mapping)


# ---------- 5 scale ----------
def scale():
    months = [date(2023, 11, 1)] + [date(2024, m, 1) for m in range(1, 13)] + [date(2025, m, 1) for m in range(1, 11)]
    months = months[1:]
    inv, sched = [], []
    for i in range(1, 3001):
        cid = f"S{i:05d}"; name = f"Scale Co {i}"; mrr = random.choice([200, 500, 900, 1500, 4000])
        for m in months:
            sched.append({"customer_id": cid, "customer_name": name, "snapshot_date": mend(m).isoformat(), "mrr": f"{mrr:.2f}", "start_date": "2023-11-01", "end_date": "", "status": "active"})
            inv.append({"invoice_id": f"{cid}-{m.strftime('%Y%m')}", "customer_id": cid, "customer_name": name, "invoice_date": m.isoformat(), "service_start": m.isoformat(), "service_end": mend(m).isoformat(), "amount": f"{mrr:.2f}", "line_type": "recurring", "description": "Subscription"})
    mapping = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapping.example.json")))
    write("scale", sched, list(sched[0].keys()), inv, list(inv[0].keys()), mapping)


if __name__ == "__main__":
    stripe(); chargebee(); quickbooks(); maxio(); scale()
