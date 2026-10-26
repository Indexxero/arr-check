#!/usr/bin/env python3
"""Checks the deferred revenue template and fill_template.py.

    pip install formulas openpyxl
    python3 templates/check_template.py <empty work folder>

The formulas are RECALCULATED by a formula engine (the `formulas` package), not read
from stored results: a copy written by fill_template.py has no stored results at all,
so a check that read them would check nothing. `formulas` is needed by this check
only; the template and fill_template.py do not use it.

Exit 0 only when, stated before any run:
  * the committed template is what build_template.py builds, and has no macros, no
    external links and no data connections;
  * filled from example/outputs (Larkspur): as of 2025-10, ending balance 0.00, ledger
    800.00, difference -800.00, and every month's closing, ledger difference and
    journal tie equal to deferred_rollforward.csv and journal.csv to the cent;
  * filled from example/quickbooks/outputs: ending balance 49,300.00, ledger and
    difference blank, the same per month agreement;
  * one journal amount changed in a filled copy makes exactly one month fail the
    journal tie, and one account changed makes the accounts check read that change;
  * fill_template.py refuses, writing nothing, a missing file, an existing output and
    a roll forward whose opening is not the month before's closing.
"""
import csv, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "deferred_revenue.xlsx")
work = os.path.abspath(sys.argv[1])
os.makedirs(work, exist_ok=True)
try:
    import formulas, openpyxl
except ImportError:
    sys.exit("this check needs the formulas and openpyxl packages: python3 -m pip install formulas openpyxl")
bad = 0

RUNS = {
    "larkspur": dict(folder="example/outputs", asof="2025-10", ending=0.0, deferred=0.0, unbilled=0.0, ledger=800.0, difference=-800.0,
                     months=12, accounts=42, lines=14,
                     # ARR-TO-GAAP-BRIDGE.md, stated before the sheet existed; = rows recomputed by the engine
                     bridge={"recurring revenue on the schedule": 72400, "less: unmatched_schedule_only": -2100, "less: over_stated": -800,
                             "= supported by invoices": 69500, "plus: under_stated, schedule shows nothing": 1400,
                             "plus: under_stated, billed above the schedule": 300, "plus: unmatched_invoice_only": 950,
                             "= invoiced recurring, spread over service periods": 72150}, recognised=72150),
    "quickbooks": dict(folder="example/quickbooks/outputs", asof="2025-10", ending=49300.0, deferred=49300.0, unbilled=0.0, ledger="", difference="",
                       months=12, accounts=10, lines=41,
                       bridge={"recurring revenue on the schedule": 12500, "less: over_stated": -1000, "= supported by invoices": 11500,
                               "= invoiced recurring, spread over service periods": 11500}, recognised=11500),
}


def report(label, ok, detail=""):
    global bad
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} {label:58s} {str(detail)[:70]}")


def cent(x):
    return x if x == "" or x is None else round(float(x), 2)


def recalc(path):
    """Every cell of the workbook as the formula engine computes it, keyed (sheet, ref)."""
    sol = formulas.ExcelModel().loads(path).finish().calculate()
    out = {}
    for k, v in sol.items():
        m = re.match(r"'\[[^\]]+\](.+)'!([A-Z]+\d+)$", k)
        if m and hasattr(v, "value"):
            val = v.value[0][0]
            out[(m.group(1).upper(), m.group(2))] = val.item() if hasattr(val, "item") else val
    return out


def fill(folder, out):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "fill_template.py"), folder, "--out", out], capture_output=True, text=True)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


# 1. The committed template is the built one, and carries nothing but cells -------------
shutil.copytree(HERE, os.path.join(work, "templates"))
subprocess.run([sys.executable, os.path.join(work, "templates", "build_template.py")], check=True, capture_output=True)
built, committed = (openpyxl.load_workbook(p) for p in (os.path.join(work, "templates", "deferred_revenue.xlsx"), TEMPLATE))
same = built.sheetnames == committed.sheetnames and all(
    [[c.value for c in row] for row in built[s].iter_rows()] == [[c.value for c in row] for row in committed[s].iter_rows()]
    for s in built.sheetnames)
report("committed template equals build_template.py output", same, ", ".join(committed.sheetnames))
with zipfile.ZipFile(TEMPLATE) as z:
    names = z.namelist()
    types = z.read("[Content_Types].xml").decode()
    every_formula = [c.value for s in committed for row in s.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
report("no macros", not any("vba" in n.lower() for n in names) and "macroEnabled" not in types, f"{len(names)} parts")
report("no external links or data connections", not any(("externalLink" in n) or ("connections" in n) for n in names)
       and not any("[" in f for f in every_formula), f"{len(every_formula)} formulas, none naming another file")

# 2. Filled from each run, recalculated, equal to the run's own files -------------------
filled = {}
for name, e in RUNS.items():
    out = os.path.join(work, f"{name}.xlsx")
    rc, last = fill(os.path.join(ROOT, e["folder"]), out)
    report(f"{name}: fill_template.py", rc == 0, last.replace(work, "<work>"))
    if rc:
        continue
    v = recalc(out)
    filled[name] = (out, v)
    T = lambda ref: v.get(("TIE OUT", ref))
    report(f"{name}: as of", T("B3") == e["asof"], T("B3"))
    for ref, key in (("B8", "ending"), ("B9", "deferred"), ("B10", "unbilled"), ("B11", "ledger"), ("B12", "difference")):
        report(f"{name}: {key}", cent(T(ref)) == e[key], f"expected {e[key]!r}, got {cent(T(ref))!r}")
    for ref, label in (("B15", "accounts less ending deferred"), ("B16", "accounts less ending unbilled"),
                       ("B17", "months failing the split check"), ("B18", "months failing the journal tie")):
        report(f"{name}: {label} is 0", cent(T(ref)) == 0, cent(T(ref)))
    report(f"{name}: months, accounts, journal lines filled", (T("B21"), T("B22"), T("B23")) == (e["months"], e["accounts"], e["lines"]),
           (T("B21"), T("B22"), T("B23")))
    roll = list(csv.DictReader(open(os.path.join(ROOT, e["folder"], "deferred_rollforward.csv"))))
    off = []
    for i, r in enumerate(roll, start=2):
        R = lambda col: v.get(("ROLL FORWARD", f"{col}{i}"))
        for col, key in (("B", "opening"), ("E", "closing"), ("J", "difference")):
            want = cent(r[key]) if key in r and r[key] != "" else ""
            if cent(R(col)) != want:
                off.append(f"{r['month']} {key} {R(col)!r} != {want!r}")
        if cent(R("L")) != 0:
            off.append(f"{r['month']} journal tie {R('L')!r}")
    report(f"{name}: every month's opening, closing, difference, tie", not off, "; ".join(off) or f"{len(roll)} months, to the cent")
    steps = {}
    for i in range(2, 62):
        step = v.get(("ARR TO REVENUE", f"C{i}"))
        if step:
            steps.setdefault(step, []).append((v.get(("ARR TO REVENUE", f"G{i}")), v.get(("ARR TO REVENUE", f"J{i}"))))
    wrong = [f"{k} {steps.get(k)} != {want}" for k, want in e["bridge"].items() if not steps.get(k) or cent(steps[k][0][0]) != want]
    report(f"{name}: ARR to revenue, each stated figure as recalculated", not wrong, "; ".join(wrong) or f"{len(e['bridge'])} figures")
    rec = [cent(g) for g, _ in steps.get("= recognised revenue, deferred_rollforward.csv", [])]
    report(f"{name}: ARR to revenue, recognised both ways", rec == [e["recognised"]] * 2, rec)
    diffs = [cent(d) for rows in steps.values() for _, d in rows if d not in ("", None)]
    report(f"{name}: ARR to revenue, every = row's difference is 0", diffs and all(d == 0 for d in diffs), f"{len(diffs)} = rows")
    report(f"{name}: tie out, sections off and residual are 0", (cent(T("B29")), cent(T("B30"))) == (0, 0), (T("B29"), T("B30")))

# 3. The checks catch a change ----------------------------------------------------------
if "larkspur" in filled:
    src, _ = filled["larkspur"]
    p = os.path.join(work, "larkspur_one_journal_line.xlsx")
    wb = openpyxl.load_workbook(src); wb["Journal"]["E3"] = wb["Journal"]["E3"].value + 1; wb.save(p)
    v = recalc(p)
    report("one journal amount +1: exactly one month fails the tie", v.get(("TIE OUT", "B18")) == 1, v.get(("TIE OUT", "B18")))
    p = os.path.join(work, "larkspur_one_account.xlsx")
    wb = openpyxl.load_workbook(src); wb["Accounts"]["C2"] = (wb["Accounts"]["C2"].value or 0) + 250; wb.save(p)
    v = recalc(p)
    report("one account deferred +250: the accounts check reads 250", cent(v.get(("TIE OUT", "B15"))) == 250.0, v.get(("TIE OUT", "B15")))
    p = os.path.join(work, "larkspur_one_bridge_step.xlsx")
    wb = openpyxl.load_workbook(src); ws = wb["ARR to revenue"]
    row = next(r for r in range(2, 62) if ws[f"C{r}"].value == "less: over_stated")
    ws[f"F{row}"] = ws[f"F{row}"].value + 100; wb.save(p)
    v = recalc(p)
    d = {v.get(("ARR TO REVENUE", f"B{r}")): cent(v.get(("ARR TO REVENUE", f"J{r}"))) for r in range(2, 62)
         if v.get(("ARR TO REVENUE", f"J{r}")) not in ("", None)}
    off = {k: x for k, x in d.items() if x != 0}
    report("one bridge step +100: only its section's difference reads 100", off == {"schedule_to_supported": 100.0}, off)
    report("one bridge step +100: the tie out counts 1 section off", v.get(("TIE OUT", "B29")) == 1, v.get(("TIE OUT", "B29")))

# 4. Refusals ---------------------------------------------------------------------------
empty = os.path.join(work, "empty_run"); os.makedirs(empty, exist_ok=True)
rc, last = fill(empty, os.path.join(work, "never_1.xlsx"))
report("refuses: a run folder with no roll forward", rc == 1 and last.startswith("REFUSED") and not os.path.exists(os.path.join(work, "never_1.xlsx")), last.replace(work, "<work>"))
rc, last = fill(os.path.join(ROOT, RUNS["larkspur"]["folder"]), os.path.join(work, "larkspur.xlsx"))
report("refuses: an output that already exists", rc == 1 and last.startswith("REFUSED"), last.replace(work, "<work>"))
broken = os.path.join(work, "broken_run"); os.makedirs(broken, exist_ok=True)
for n in ("deferred_rollforward.csv", "deferred_accounts.csv", "journal.csv"):
    shutil.copy(os.path.join(ROOT, RUNS["larkspur"]["folder"], n), broken)
rows = list(csv.reader(open(os.path.join(broken, "deferred_rollforward.csv"))))
rows[3][1] = str(float(rows[3][1]) + 1)
csv.writer(open(os.path.join(broken, "deferred_rollforward.csv"), "w", newline="")).writerows(rows)
rc, last = fill(broken, os.path.join(work, "never_2.xlsx"))
report("refuses: an opening that is not the prior closing", rc == 1 and last.startswith("REFUSED") and not os.path.exists(os.path.join(work, "never_2.xlsx")), last.replace(work, "<work>"))

# 5. Text from a run stays text ---------------------------------------------------------
eq = os.path.join(work, "equals_run"); os.makedirs(eq, exist_ok=True)
for n in ("deferred_rollforward.csv", "deferred_accounts.csv", "journal.csv", "arr_to_revenue.csv"):
    shutil.copy(os.path.join(ROOT, RUNS["larkspur"]["folder"], n), eq)
rows = list(csv.reader(open(os.path.join(eq, "journal.csv"))))
rows[1][1] = "=1+1"
csv.writer(open(os.path.join(eq, "journal.csv"), "w", newline="")).writerows(rows)
rc, last = fill(eq, os.path.join(work, "equals.xlsx"))
c = openpyxl.load_workbook(os.path.join(work, "equals.xlsx"))["Journal"]["B2"] if rc == 0 else None
report("a customer named =1+1 is written as text, not a formula", c is not None and c.data_type == "s" and c.value == "=1+1",
       None if c is None else (c.data_type, c.value))

print("RESULT:", "ALL AS STATED" if not bad else f"{bad} NOT AS STATED")
sys.exit(1 if bad else 0)
