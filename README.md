# arr-check

A second pass on a SaaS customer ARR schedule, against the invoice lines, on one laptop. Two exports in, a folder of findings out. Nothing is uploaded anywhere.

It answers one question per customer per month: do the invoices support the recurring revenue the schedule claims? Where they do not, it says by how much and names the likely cause. It does not replace a Quality of Earnings review, it gives no accounting opinion, and it does not decide which figure is right. It makes the disagreement specific.

A worked example on a fictional company, with every output file: https://measure.indexxero.com/example

Or run it in a browser tab, nothing leaving the tab: https://measure.indexxero.com/run

## What comes out of one run

From the customer schedule and the invoice export, in about ten seconds:

* `exceptions.csv` and `accounts.csv`: every account where the invoices do not support the schedule, with the amount and the likely cause (over stated, under stated, timing, credit or rebill, duplicate invoice, ramp, classification, unmatched).
* `bridge.csv`: the ARR bridge (new, expansion, contraction, churn) on the schedule, on the invoices and on the supported figure, with the difference row.
* `deferred_rollforward.csv` and `journal.csv`: the deferred revenue the invoices imply, month by month, and the month end entry a QuickBooks Online user posts by hand today. Works on QuickBooks exports, which carry no service period.
* `arr_to_revenue.csv`: for the as of month, schedule MRR to supported MRR to invoiced recurring to the roll forward's recognised revenue, one row per bucket with the accounts behind it, and billings to recognised through the deferred movement. Read from `compare_customer_month.csv` and `deferred_rollforward.csv`, not worked a second way; any gap is a row named residual. `python3 example/check_arr_to_revenue.py` checks it in every example.
* `closepack.md`: one page for the board deck or a buyer, with what changed since last month when the previous run is given.
* `receipt.json`: the hash of every input and output, so anyone with the same files can confirm the run with `python3 receipt.py verify`.

## A deferred revenue template

`templates/deferred_revenue.xlsx` is a blank roll forward, account schedule and journal with the tie out built in as formulas; no macros, no links to other files. `python3 fill_template.py out --out filled.xlsx` fills a copy from a run. `python3 templates/check_template.py <empty folder>` (needs `pip install formulas`) recalculates every formula and checks it against the run. The committed file's bytes differ from a rebuild by `templates/build_template.py` (timestamps, and how a given openpyxl writes empty tags); the check compares every cell and formula, not the hash.

## What it needs

Two files, csv or xlsx, from any system. Column names are mapped in a small json, so the exports can come from Stripe, Chargebee, Maxio, QuickBooks, NetSuite, HubSpot, Salesforce or a spreadsheet.

1. The customer schedule: the list used when ARR or MRR is stated. One row per customer per month (`snapshot`), one row per customer with start and end dates (`contract`), or one column per month (`wide`).
2. The invoice lines: every line for the same customers over the same months, credit memos included. Invoice id, customer, invoice date, service period, amount, line type.

Python 3.9 or later, pandas and openpyxl. No other dependency. No network call anywhere in the code; read it.

## Run it

```
pip install pandas openpyxl
cp mapping.example.json mapping.json      # put the export's column names in; leave "" where a column does not exist
python3 pilot.py --schedule schedule.csv --invoices invoices.csv --map mapping.json --asof 2025-10 --out out
```

`--asof` is the month the figures are stated as of. Add `--profile` to stop after the profile and see what the files can support before any number is computed.

## Finance answers

Add `--answers answers.json` to disclose per-customer-month finance decisions on a rerun.
```json
{"answers": [{"customer_key": "...", "month": "2025-10", "decision": "accepted|explained|disputed", "reason": "contract_amendment|credit_memo|billing_error|schedule_error|reseller_child|test_account|other", "note": "free text", "by": "initials", "date": "2025-11-02"}]}
```
`explained` keeps schedule MRR and labels the exception; `accepted` labels the kit result; `disputed` changes nothing.

To see it work in a minute on the fictional set:

```
sh run_example.sh
```

## What comes out

| file | what |
|---|---|
| `manifest.json` | sha256, rows and columns of each input, the mapping used, warnings |
| `profile.md` | blanks, distinct values, unparsed dates and amounts, duplicate ids |
| `match_table.csv` | one row per customer, the method used to match, the confidence |
| `invoice_lines_classified.csv` | every invoice line with its kind: recurring, credit, non_recurring, unknown_type |
| `invoice_mrr_monthly.csv` | invoice supported MRR per customer per month, credits netted |
| `compare_customer_month.csv` | schedule MRR beside invoice MRR, the difference, the bucket |
| `exceptions.csv` | the rows of the above that are not supported |
| `accounts.csv` | one row per customer, unresolved MRR as of the month, dominant cause |
| `retention.csv` | GRR and NRR over the window on three bases: schedule, invoices, supported |
| `cohorts.csv` | revenue retained at twelve months by start quarter, two bases |
| `report.md` | the findings in prose and tables |
| `pilot.xlsx` | all of the above as sheets, for hand review |
| `supported_export.csv` | the supported schedule, one row per account |
| `bridge.csv`, `bridge_accounts.csv` | the monthly ARR bridge on three bases, and the accounts behind each movement |
| `deferred_rollforward.csv`, `deferred_accounts.csv`, `journal.csv` | deferred revenue implied by the invoices, per month and per account, and the month end entry |
| `closepack.md` | the one page for the board deck; see The close pack |
| `receipt.json` | sha256 of inputs, mapping, pilot.py and every output; see The receipt |

## The receipt

Every run also writes `receipt.json`: the sha256 of the two inputs, the mapping, `pilot.py` itself and every output file, with the kit version and the parameters. Anyone holding the same files can recompute it:

```
python3 receipt.py verify --out out --schedule schedule.csv --invoices invoices.csv --map mapping.json
```

When the run used a ledger balance file or an answers file, pass the same `--deferred-gl` or `--answers` to `verify`: they change outputs, so the receipt records them as inputs. It prints `RECEIPT OK`, or one `MISMATCH` line per file that differs. It proves that these exact files, run by this exact code, produced these exact outputs. It does not prove that the method is right or that the inputs are true. A company can run the kit itself and send the receipt and the register to an advisor; the advisor reruns on the same files and compares. The data never has to move.

## The ARR bridge, three ways

`bridge.csv` is the monthly bridge a board deck carries: start, new, reactivation, expansion, contraction, churn, end. It is computed on three bases from the same customer months: the schedule the company reports, the invoice lines on their own, and the supported figure. A `difference` row (schedule minus supported) shows where the two disagree, and `bridge_accounts.csv` names the accounts behind every movement. New means first MRR in the window; reactivation means MRR after a gap; churn means MRR last month and none this month. The identity start + new + reactivation + expansion minus contraction minus churn = end is asserted for every month, and the run stops if it fails.

## Deferred revenue implied by the invoices

The kit already spreads every recurring line over its service period, so billed minus recognised is already computed; this writes it out. `deferred_rollforward.csv` gives opening, billings, recognised and closing for each month, and the identity opening plus billings minus recognised equals closing is asserted, not assumed. `deferred_accounts.csv` gives the closing position per customer at the as of month, with months of cover where there is any. `journal.csv` is a schedule a controller can post from, with the accounts named in plain words and the invoice ids in the memo.

Deferred and unbilled are reported apart and never netted: a book with money on both sides would otherwise read as nil. Pass `--deferred-gl deferred_gl.csv` with columns `month,balance` to compare against the company's own balance; without it the report says the ledger was not provided rather than guessing at one. This is not a posting, not a chart of accounts and no opinion on revenue recognition policy.

## QuickBooks Online, and invoices with no service period

QuickBooks Online invoice exports carry no service period, so an annual invoice would otherwise land in one month and no deferred revenue would ever show. With the rule `"periodless_recurring": "whole_months_from_schedule"` in the mapping, a recurring line with no period gets one only when its amount is an exact whole multiple of that customer's schedule MRR (within tolerance), 2 to 36 months, starting in the invoice month. A discounted or odd amount is not guessed at: it stays in its invoice month and is flagged. Every line given a period this way says so in `invoice_lines_classified.csv` (`period_source = inferred_from_schedule`), and the manifest counts them.

`journal.csv` is the month end entry a QuickBooks user posts by hand today: QuickBooks books an invoice to income, so the entry is one adjustment per customer that moves the deferred balance to where the invoices say it should be. A customer billed for the same month has no line. The journal ties to the roll forward in every month.

`example/quickbooks/` is a fictional QuickBooks shaped pair (`python3 gen_quickbooks.py`) with monthly, quarterly and annual customers and one discounted annual. The expected deferred balance at 2025-10 is 49,300, stated in the generator, and the kit reproduces it account by account.

## Month over month

A fractional CFO runs the kit every month; the question after the second run is what changed. `python3 diff_runs.py --before out_oct --after out_nov --out diff_nov` compares the two `accounts.csv` files and writes `accounts_diff.csv` (one row per customer: new, changed, persisted, resolved, unchanged_supported, with the unresolved MRR and cause on both sides) and `summary.md` (counts, the movement in unresolved MRR, the largest new and resolved, every cause change). `python3 gen_next_month.py` makes the Larkspur set one month later with four planted changes and an `expected.json`; the diff reproduces it: new 1, resolved 2, changed 1.

## The close pack

`closepack.md` is the one page a fractional CFO attaches to the board deck or hands a buyer, written by every run from files the run already wrote: reported against supported ARR, the bridge over the window, retention three ways, cohorts, concentration, the ten largest exceptions, the deferred revenue position against the ledger when given, what changed since the previous run (pass `--before <previous out folder>`), and the hashes of the run that made it. No chart, no opinion.

## How the numbers are made

* Customers are matched by id first, then by normalised name, then by fuzzy name (ratio 0.88 or above, marked for review). Unmatched on either side is a finding, not an error.
* Recurring invoice lines are spread over their service period. Whole months split evenly, so an annual prepay is the same every month. Part months split by days. A line with no service period lands in its invoice month and is flagged.
* Credits are netted into the month they belong to. Non recurring lines (services, setup, usage) are kept out of MRR and listed. A line whose type is not recognised is flagged `unknown_type`.
* Supported MRR for a customer month is the schedule figure where the invoices back it within tolerance (1 percent or 5 currency units, whichever is larger, set in the mapping), and the lower of the two where they do not.
* Buckets, in the order tested: unmatched, duplicate invoice id, credit in the month, unknown line type, within tolerance (supported), timing (the difference nets against the month before or after, or the lines have no service period), ramp (first months, schedule above invoices), then over stated or under stated.
* GRR over the window: for the accounts in the starting month, the sum of the lower of start and end MRR, over the starting book. NRR: end MRR of the same accounts over the starting book.

Every step writes a file, so each figure can be traced to the rows behind it. The bucket is a first sort, not a verdict.

## What it does not do

It does not read contracts, order forms, the general ledger, bank records or deferred revenue. It covers one leg of the usual three (schedule to invoices). It does not convert currencies; more than one currency raises a warning. It records reseller parents and children, it does not roll them up. It has been tested on synthetic exports in five shapes (`run_stress.sh`) and on no real company's data as of this version.

## Data

Real customer data should stay on the machine it is on. Nothing in this repository sends data anywhere, and nothing should be pasted into a chat tool to ask about it. Questions about the kit are best asked with the fictional set in `example/` or with made up rows.

## Contributing

An export shape that breaks the kit is the most useful thing to send: a few synthetic rows in the same shape, the mapping used, and the traceback. Please never attach a real export, even a redacted one. Changes are listed in `CHANGES.md` with the date and the reason.

Indexxero, Inc., Dallas, Texas. MIT licence.
