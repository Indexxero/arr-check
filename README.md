# arr-check

A second pass on a SaaS customer ARR schedule, against the invoice lines, on one laptop. Two exports in, a folder of findings out. Nothing is uploaded anywhere.

It answers one question per customer per month: do the invoices support the recurring revenue the schedule claims? Where they do not, it says by how much and names the likely cause. It does not replace a Quality of Earnings review, it gives no accounting opinion, and it does not decide which figure is right. It makes the disagreement specific.

A worked example on a fictional company, with every output file: https://measure.indexxero.com/example

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
| `receipt.json` | sha256 of inputs, mapping, pilot.py and every output; see The receipt |

## The receipt

Every run also writes `receipt.json`: the sha256 of the two inputs, the mapping, `pilot.py` itself and every output file, with the kit version and the parameters. Anyone holding the same files can recompute it:

```
python3 receipt.py verify --out out --schedule schedule.csv --invoices invoices.csv --map mapping.json
```

It prints `RECEIPT OK`, or one `MISMATCH` line per file that differs. It proves that these exact files, run by this exact code, produced these exact outputs. It does not prove that the method is right or that the inputs are true. A company can run the kit itself and send the receipt and the register to an advisor; the advisor reruns on the same files and compares. The data never has to move.

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
