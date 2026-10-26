#!/usr/bin/env python3
"""Builds templates/deferred_revenue.xlsx, the blank deferred revenue template.

    python3 templates/build_template.py

The workbook is built here rather than edited by hand so that every formula is in one
readable place and the committed file can be rebuilt. openpyxl only; no macros, no
external links, no named ranges pointing outside the workbook.

FIVE SHEETS
  Read me       how to fill it, in words
  Tie out       the as of month, the ending balance, and the checks that must read 0
  Roll forward  one row per month: opening, billings, recognised, closing, the split
                into deferred and unbilled, the ledger balance and the journal tie
  Accounts      one row per account at the as of month
  Journal       the month end lines, one per account per month

Yellow cells are typed in (or written by fill_template.py); every other figure is a
formula. Only SUM, SUMIFS, COUNTIFS, COUNTA, IF, OR, ROUND, INDEX, MATCH and IFERROR are used,
all of which Excel and Google Sheets both have.
"""
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "deferred_revenue.xlsx")

MONTHS, ACCOUNTS, LINES = 60, 5000, 50000      # capacity; fill_template.py refuses beyond it
R_LAST, A_LAST, J_LAST = 1 + MONTHS, 1 + ACCOUNTS, 1 + LINES
MONEY = '#,##0.00;-#,##0.00;0.00'
INPUT = PatternFill("solid", fgColor="FFF2CC")
BOLD = Font(bold=True)

wb = Workbook()
readme = wb.active
readme.title = "Read me"
tie = wb.create_sheet("Tie out")
roll = wb.create_sheet("Roll forward")
acc = wb.create_sheet("Accounts")
jnl = wb.create_sheet("Journal")


def header(ws, names, widths):
    for i, (n, w) in enumerate(zip(names, widths), start=1):
        c = ws.cell(row=1, column=i, value=n)
        c.font = BOLD
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = "A2"


# Roll forward ---------------------------------------------------------------------------
header(roll, ["Month (yyyy-mm, text)", "Opening", "Billings", "Recognised", "Closing",
              "Closing deferred", "Closing unbilled", "Split check (deferred less unbilled less closing)",
              "Ledger balance", "Difference (closing less ledger)", "Journal movement", "Journal tie (movement less change)"],
       [14, 14, 14, 14, 14, 14, 14, 18, 14, 16, 14, 18])
J = lambda col: f"Journal!${col}$2:${col}${J_LAST}"
DEF, UNB = "'Tie out'!$B$5", "'Tie out'!$B$6"
for r in range(2, R_LAST + 1):
    a = f"$A{r}"
    roll.cell(row=r, column=1).number_format = "@"
    for col in "ACDFGI":
        roll[f"{col}{r}"].fill = INPUT
    if r == 2:
        roll["B2"].fill = INPUT
    else:
        roll[f"B{r}"] = f'=IF({a}="","",E{r - 1})'
    roll[f"E{r}"] = f'=IF({a}="","",ROUND(B{r}+C{r}-D{r},2))'
    roll[f"H{r}"] = f'=IF({a}="","",ROUND(F{r}-G{r}-E{r},2))'
    roll[f"J{r}"] = f'=IF(OR({a}="",I{r}=""),"",ROUND(E{r}-I{r},2))'
    # Credits to deferred and debits from unbilled raise the net balance; the reverse lowers it.
    roll[f"K{r}"] = (f'=IF({a}="","",ROUND(SUMIFS({J("E")},{J("A")},{a},{J("D")},{DEF})'
                     f'-SUMIFS({J("E")},{J("A")},{a},{J("C")},{DEF})'
                     f'+SUMIFS({J("E")},{J("A")},{a},{J("D")},{UNB})'
                     f'-SUMIFS({J("E")},{J("A")},{a},{J("C")},{UNB}),2))')
    roll[f"L{r}"] = f'=IF({a}="","",ROUND(K{r}-(E{r}-B{r}),2))'
    for col in "BCDEFGHIJKL":
        roll[f"{col}{r}"].number_format = MONEY

# Accounts -------------------------------------------------------------------------------
header(acc, ["Account key", "Customer name", "Closing deferred", "Closing unbilled", "Months of deferred cover"],
       [22, 32, 16, 16, 14])
for r in range(2, A_LAST + 1):
    for col in "ABCDE":
        acc[f"{col}{r}"].fill = INPUT
    acc[f"C{r}"].number_format = acc[f"D{r}"].number_format = MONEY

# Journal --------------------------------------------------------------------------------
header(jnl, ["Month (yyyy-mm, text)", "Customer name", "Debit account", "Credit account", "Amount", "Memo"],
       [14, 32, 22, 22, 14, 40])
for r in range(2, J_LAST + 1):
    jnl.cell(row=r, column=1).number_format = "@"
    jnl[f"E{r}"].number_format = MONEY

# Tie out --------------------------------------------------------------------------------
tie.column_dimensions["A"].width = 58
tie.column_dimensions["B"].width = 18
tie.column_dimensions["C"].width = 60
R = lambda col: f"'Roll forward'!${col}$2:${col}${R_LAST}"
# INDEX of an empty cell reads as 0, so a month with no ledger balance would show a
# ledger balance of 0; the outer IF keeps it blank instead.
pick = lambda col: f'INDEX({R(col)},MATCH($B$3,{R("A")},0))'
at = lambda col: f'=IF($B$3="","",IFERROR(IF({pick(col)}="","",{pick(col)}),"as of month not in Roll forward"))'
rows = [
    ("Deferred revenue tie out", None, None),
    (None, None, None),
    ("As of month (yyyy-mm, text)", "", "typed in; the month every figure below is read at"),
    (None, None, None),
    ("Journal account for deferred revenue", "Deferred revenue", "as named in Journal, columns C and D"),
    ("Journal account for unbilled revenue", "Unbilled revenue", "as named in Journal, columns C and D"),
    (None, None, None),
    ("Ending balance (deferred less unbilled)", at("E"), "Roll forward, Closing, at the as of month"),
    ("Ending deferred", at("F"), None),
    ("Ending unbilled", at("G"), None),
    ("Ledger balance", at("I"), "blank when no ledger balance was given"),
    ("Difference (ending balance less ledger)", at("J"), "blank when no ledger balance was given"),
    (None, None, None),
    ("Checks that should read 0", None, None),
    ("Accounts: deferred less ending deferred", '=IF($B$3="","",IFERROR(ROUND(SUM(Accounts!$C$2:$C$%d)-B9,2),""))' % A_LAST, "the accounts sum to the roll forward"),
    ("Accounts: unbilled less ending unbilled", '=IF($B$3="","",IFERROR(ROUND(SUM(Accounts!$D$2:$D$%d)-B10,2),""))' % A_LAST, None),
    ("Months where deferred less unbilled is not the closing", f'=COUNTIFS({R("H")},">0.005")+COUNTIFS({R("H")},"<-0.005")', "Roll forward, column H"),
    ("Months where the journal does not move the balance by the change", f'=COUNTIFS({R("L")},">0.005")+COUNTIFS({R("L")},"<-0.005")', "Roll forward, column L"),
    (None, None, None),
    ("Totals", None, None),
    ("Months filled", f'=COUNTA({R("A")})', None),
    ("Accounts filled", '=COUNTA(Accounts!$A$2:$A$%d)' % A_LAST, None),
    ("Journal lines filled", '=COUNTA(Journal!$A$2:$A$%d)' % J_LAST, None),
    ("Journal amount", '=SUM(Journal!$E$2:$E$%d)' % J_LAST, None),
    (None, None, None),
    ("Filled from", "", "written by fill_template.py; blank when typed by hand"),
]
for i, (label, value, note) in enumerate(rows, start=1):
    if label:
        tie.cell(row=i, column=1, value=label)
    if value is not None:
        tie.cell(row=i, column=2, value=value)
    if note:
        tie.cell(row=i, column=3, value=note)
tie["A1"].font = Font(bold=True, size=14)
tie["A14"].font = tie["A20"].font = BOLD
for ref in ("B3", "B5", "B6", "B26"):
    tie[ref].fill = INPUT
tie["B3"].number_format = "@"
for r in (8, 9, 10, 11, 12, 15, 16, 24):
    tie[f"B{r}"].number_format = MONEY

# Read me --------------------------------------------------------------------------------
readme.column_dimensions["A"].width = 110
text = [
    "Deferred revenue roll forward template",
    "",
    "What it is",
    "A month by month roll forward of deferred revenue, a schedule of the balance by account at one month,",
    "and the month end journal, tied to each other and to the general ledger balance.",
    "",
    "How to fill it",
    "1. Roll forward: one row per month, oldest first. Type the month as text, yyyy-mm, for example 2025-10.",
    "   Type the opening balance in the first row only; every later opening is the month before's closing.",
    "   Type billings, recognised, closing deferred, closing unbilled and, if known, the ledger balance.",
    "2. Accounts: one row per account, its closing deferred and unbilled at the as of month.",
    "3. Journal: the month end lines. Amounts are positive; the debit and credit accounts say which way.",
    "4. Tie out: type the as of month. The account names for deferred and unbilled revenue must match",
    "   the names used in the Journal sheet.",
    "",
    "Yellow cells are typed in. Every other figure is a formula and recalculates when a yellow cell changes.",
    "",
    "What the checks mean",
    "Closing is opening plus billings less recognised. Closing deferred less closing unbilled must equal it.",
    "The journal for a month must move the net balance by exactly the change from opening to closing.",
    "The accounts must sum to the roll forward at the as of month.",
    "Any check that does not read 0 names a figure to look at; the template does not say which side is right.",
    "",
    "Capacity: %d months, %d accounts, %d journal lines." % (MONTHS, ACCOUNTS, LINES),
    "",
    "Filling it from an arr-check run",
    "python3 fill_template.py <run folder> --out deferred_revenue_filled.xlsx",
    "reads deferred_rollforward.csv, deferred_accounts.csv and journal.csv from the run folder.",
    "",
    "This is a schedule to check and post from. It is not an opinion on revenue recognition policy.",
    "No macros, no links to other files.",
]
for i, line in enumerate(text, start=1):
    readme.cell(row=i, column=1, value=line)
for r in (1, 3, 7, 18, 26):
    readme[f"A{r}"].font = Font(bold=True, size=14 if r == 1 else 11)

wb.active = 1                                       # opens on Tie out
wb.calculation.fullCalcOnLoad = True                # Excel and Sheets compute on open
wb.save(OUT)
print(f"wrote {os.path.relpath(OUT)}: {MONTHS} months, {ACCOUNTS} accounts, {LINES} journal lines of capacity")
