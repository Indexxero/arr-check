# Pilot findings, as of 2025-10

Inputs: schedule `schedule.csv` (521 rows), invoices `invoices.csv` (511 lines). Hashes in manifest.json. Kit 2026-10-24.

## Totals

| | ARR |
|---|---:|
| Reported on the schedule | 868,800 |
| Supported by invoices | 834,000 |
| Unresolved, needs review | 34,800 |
| Accounts on the schedule | 37 |
| Accounts with an exception in the last 12 months | 10 |

## Exceptions by cause

| cause | accounts | unresolved ARR |
|---|---:|---:|
| unmatched_schedule_only | 1 | 25,200 |
| over_stated | 1 | 9,600 |
| duplicate_invoice | 1 | 0 |
| explained_credit_memo | 1 | 0 |
| explained_other | 1 | 0 |
| ramp_or_proration | 1 | 0 |
| timing | 1 | 0 |
| under_stated | 2 | 0 |
| unmatched_invoice_only | 1 | 0 |

What each cause means: supported, the invoices back the schedule within tolerance. over_stated, the schedule carries more than the invoices show. under_stated, the invoices show more than the schedule. timing, the same money lands a month earlier or later. credit_or_rebill, a credit memo or rebill touched the month. duplicate_invoice, the same invoice id appears twice. ramp_or_proration, the first months bill below the schedule. classification, a non recurring or untyped line sits where recurring revenue is expected. unmatched_schedule_only, no invoices found for the account. unmatched_invoice_only, invoices with no account on the schedule.

## Retention, three ways

| basis | from | to | starting book MRR | accounts | GRR | NRR |
|---|---|---|---:|---:|---:|---:|
| schedule | 2024-10 | 2025-10 | 75,800 | 41 | 84.2 | 85.0 |
| invoices | 2024-10 | 2025-10 | 69,400 | 38 | 84.7 | 84.7 |
| supported | 2024-10 | 2025-10 | 69,100 | 38 | 82.6 | 82.6 |

Schedule is what the company reports. Invoices is what the billing lines support on their own. Supported keeps the schedule figure wherever the invoices back it and drops to the invoice figure where they do not.

## Cohorts, revenue retained at 12 months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q4 | 41 | 85.0 | 89.0 |

## ARR bridge, three ways

Schedule is what the company reports. Invoices is what the billing lines show on their own. Supported keeps the schedule figure where the invoices back it. Difference is schedule minus supported. Figures are ARR (MRR times 12). Every movement traces to its accounts in bridge_accounts.csv.

### As of 2025-10

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 868,800 | 0 | 0 | 0 | 0 | 0 | 868,800 |
| invoices | 865,800 | 0 | 0 | 0 | 0 | 0 | 865,800 |
| supported | 834,000 | 0 | 0 | 0 | 0 | 0 | 834,000 |
| difference | 34,800 | 0 | 0 | 0 | 0 | 0 | 34,800 |

### Window 2024-11 to 2025-10, movements summed

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 909,600 | 96,000 | 0 | 7,200 | 4,800 | 139,200 | 868,800 |
| invoices | 832,800 | 105,000 | 0 | 75,600 | 25,200 | 122,400 | 865,800 |
| supported | 829,200 | 93,600 | 0 | 55,200 | 4,800 | 139,200 | 834,000 |
| difference | 80,400 | 2,400 | 0 | -48,000 | 0 | 0 | 34,800 |

The largest difference between the two bases over the window is in expansion: 48,000 ARR. The schedule and the invoices disagree most about that movement.

## Accounts to review first

| account | schedule MRR | invoice MRR | unresolved MRR | cause | months not supported |
|---|---:|---:|---:|---|---:|
| Silent Partner Inc | 2,100 | 0 | 2,100 | unmatched_schedule_only | 12 |
| Granite Peak Software | 5,000 | 4,200 | 800 | over_stated | 12 |
| Quiet Creek Software | 1,000 | 1,300 | 0 | under_stated | 12 |
| Orphan Billing LLC | 0 | 950 | 0 | unmatched_invoice_only | 9 |
| Juniper Ridge Labs | 8,000 | 8,000 | 0 | ramp_or_proration | 3 |
| Lantern Field Co | 0 | 1,400 | 0 | under_stated | 2 |
| Cedar Loop Systems | 3,000 | 3,000 | 0 | explained_credit_memo | 1 |
| Northwind Dynamics | 2,400 | 2,400 | 0 | timing | 1 |
| Maple Street Health | 2,600 | 2,600 | 0 | explained_other | 1 |
| Harbor Light Media | 1,700 | 1,700 | 0 | duplicate_invoice | 1 |

## Answered exceptions

| customer key | month | decision | reason | prior bucket | result bucket | note | by | date | status |
|---|---|---|---|---|---|---|---|---|---|
| F-002 | 2025-10 | accepted | schedule_error | over_stated | over_stated_accepted | Schedule should be corrected to the billed amount. | LP | 2025-11-02 | applied |
| F-003 | 2025-06 | explained | credit_memo | credit_or_rebill | explained_credit_memo | Credit and rebill were documented for the same service period. | LP | 2025-11-02 | applied |
| F-008 | 2025-03 | explained | other | classification | explained_other | Usage classification was reviewed and does not change recurring support. | LP | 2025-11-02 | applied |
| F-007 | 2025-10 | disputed | other | unmatched_schedule_only | unmatched_schedule_only | Finance disputes the missing-invoice finding pending source-system review. | LP | 2025-11-02 | applied |

Overridden by answers: 2 customer months, 0 MRR


## Matching

Exact id: 40. Normalised name: 1. Ambiguous: 0. Schedule only: 1. Invoices only: 1. Full table in match_table.csv.

## What the files cannot support

Invoice lines with no type the kit could classify: 1. Lines with no service period (spread to the invoice month instead): 14. Mapping warnings: 1.

The kit does not read contracts, order forms, the general ledger or bank records. Where the schedule and the invoices disagree, the kit shows the disagreement and the lines behind it. Which figure is right is a question for the company's finance lead, and in a transaction for the diligence team. Nothing here is an accounting opinion.

## Questions for finance

* Where are the invoices for the accounts with none?
* Which accounts carry schedule MRR above the invoices, and is there a contract or a billing gap behind each one?
* Are the duplicate invoice ids a true double bill or an export artefact?
* Do the first months bill below the schedule by contract (ramp) or by proration, and should the schedule show the ramp?
* Is invoice timing a month off by design (billing in arrears) or by accident?
* Which accounts bill above the schedule, and is the schedule stale or the billing wrong?
* Which billed accounts are missing from the schedule, and why?
