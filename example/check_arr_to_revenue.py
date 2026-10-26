#!/usr/bin/env python3
"""Checks arr_to_revenue.csv in every committed example against figures stated before
pilot.py wrote the file, and against the two files it must read from.

    python3 example/check_arr_to_revenue.py

Per example, exit 0 only when:
  * every named step has the stated amount (monthly, the as of month);
  * no row is a residual;
  * in each section the opening figure plus its steps reaches its = row to the cent;
  * the = rows equal the column sums of compare_customer_month.csv (sched_mrr,
    supported_mrr, inv_mrr) and the roll forward's recognised, read from those files.
Standard library only.
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Stated 2026-10-26 from the existing outputs, before pilot.py changed.
LARKSPUR = {"recurring revenue on the schedule": 72400, "less: unmatched_schedule_only": -2100, "less: over_stated": -800,
            "= supported by invoices": 69500, "plus: under_stated, schedule shows nothing": 1400,
            "plus: under_stated, billed above the schedule": 300, "plus: unmatched_invoice_only": 950,
            "= invoiced recurring, spread over service periods": 72150, "billed in the month, recurring and credit lines": 70150,
            "plus: released from the net deferred balance (2,000.00 to 0.00)": 2000}
EXPECTED = {
    "outputs": ("2025-10", LARKSPUR, 72150),
    "outputs_answered": ("2025-10", {**{k: v for k, v in LARKSPUR.items() if k != "less: over_stated"},
                                     "less: over_stated_accepted": -800}, 72150),
    "quickbooks/outputs": ("2025-10", {"recurring revenue on the schedule": 12500, "less: over_stated": -1000, "= supported by invoices": 11500,
                                       "= invoiced recurring, spread over service periods": 11500, "billed in the month, recurring and credit lines": 42800,
                                       "less: added to the net deferred balance (18,000.00 to 49,300.00)": -31300}, 11500),
    "next_month/out": ("2025-11", {"recurring revenue on the schedule": 71600, "less: unmatched_schedule_only": -2100, "= supported by invoices": 69500,
                                   "plus: timing": 2400, "plus: under_stated, schedule shows nothing": 1400, "plus: under_stated, billed above the schedule": 300,
                                   "plus: unmatched_invoice_only": 3050, "= invoiced recurring, spread over service periods": 76650,
                                   "billed in the month, recurring and credit lines": 98650,
                                   "less: added to the net deferred balance (0.00 to 22,000.00)": -22000}, 76650),
}
bad = 0


def report(label, ok, detail=""):
    global bad
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} {label:64s} {detail}")


for folder, (asof, steps, recognised) in EXPECTED.items():
    d = os.path.join(HERE, folder)
    rows = list(csv.DictReader(open(os.path.join(d, "arr_to_revenue.csv"))))
    got = {r["step"]: float(r["amount"]) for r in rows}
    for step, want in steps.items():
        report(f"{folder}: {step}", round(got.get(step, float("nan")), 2) == want, f"expected {want:,.2f}, got {got.get(step)}")
    rec_rows = [r for r in rows if r["step"].startswith("= recognised revenue")]
    report(f"{folder}: recognised, both ways", len(rec_rows) == 2 and all(float(r["amount"]) == recognised for r in rec_rows),
           [r["amount"] for r in rec_rows])
    res = [r for r in rows if r["bucket"] == "residual"]
    report(f"{folder}: no residual row", not res, "; ".join(f"{r['section']} {r['amount']}" for r in res))
    # Each section starts from its own opening row (no bucket, not an = row) or, without
    # one, from the = row before it; its steps must reach its = row to the cent.
    carried, off = 0.0, []
    for section in dict.fromkeys(r["section"] for r in rows if r["section"] != "memo"):
        sec = [r for r in rows if r["section"] == section]
        opening = [r for r in sec if not r["bucket"] and not r["step"].startswith("=")]
        total = float(opening[0]["amount"]) if opening else carried
        total += sum(float(r["amount"]) for r in sec if r["bucket"])
        end = float([r for r in sec if r["step"].startswith("=")][-1]["amount"])
        if round(total - end, 2) != 0:
            off.append(f"{section} steps reach {total:,.2f}, = row {end:,.2f}")
        carried = end
    report(f"{folder}: every section's steps reach its = row", not off, "; ".join(off))
    cmp = [r for r in csv.DictReader(open(os.path.join(d, "compare_customer_month.csv"))) if r["month"] == asof]
    roll = [r for r in csv.DictReader(open(os.path.join(d, "deferred_rollforward.csv"))) if r["month"] == asof][0]
    for step, col in (("recurring revenue on the schedule", "sched_mrr"), ("= supported by invoices", "supported_mrr"),
                      ("= invoiced recurring, spread over service periods", "inv_mrr")):
        s = round(sum(float(r[col]) for r in cmp), 2)
        report(f"{folder}: {step} = compare_customer_month.csv {col}", got.get(step) == s, f"{got.get(step)} vs {s}")
    report(f"{folder}: recognised = deferred_rollforward.csv", float(rec_rows[0]["amount"]) == float(roll["recognised"]) if rec_rows else False, roll["recognised"])
print("RESULT:", "ALL AS STATED" if not bad else f"{bad} NOT AS STATED")
sys.exit(1 if bad else 0)
