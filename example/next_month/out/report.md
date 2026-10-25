# Pilot findings, as of 2025-11

Inputs: schedule `schedule.csv` (558 rows), invoices `invoices.csv` (549 lines). Hashes in manifest.json. Kit 2026-10-25.

## Totals

| | ARR |
|---|---:|
| Reported on the schedule | 859,200 |
| Supported by invoices | 834,000 |
| Unresolved, needs review | 25,200 |
| Accounts on the schedule | 37 |
| Accounts with an exception in the last 12 months | 9 |

## Exceptions by cause

| cause | accounts | unresolved ARR |
|---|---:|---:|
| unmatched_schedule_only | 1 | 25,200 |
| credit_or_rebill | 1 | 0 |
| over_stated | 1 | 0 |
| ramp_or_proration | 1 | 0 |
| timing | 1 | 0 |
| under_stated | 2 | 0 |
| unmatched_invoice_only | 2 | 0 |

What each cause means: supported, the invoices back the schedule within tolerance. over_stated, the schedule carries more than the invoices show. under_stated, the invoices show more than the schedule. timing, the same money lands a month earlier or later. credit_or_rebill, a credit memo or rebill touched the month. duplicate_invoice, the same invoice id appears twice. ramp_or_proration, the first months bill below the schedule. classification, a non recurring or untyped line sits where recurring revenue is expected. unmatched_schedule_only, no invoices found for the account. unmatched_invoice_only, invoices with no account on the schedule.

## Retention, three ways

| basis | from | to | starting book MRR | accounts | GRR | NRR |
|---|---|---|---:|---:|---:|---:|
| schedule | 2024-11 | 2025-11 | 75,800 | 41 | 83.1 | 83.9 |
| invoices | 2024-11 | 2025-11 | 73,200 | 40 | 85.5 | 89.6 |
| supported | 2024-11 | 2025-11 | 72,900 | 40 | 83.5 | 84.4 |

Schedule is what the company reports. Invoices is what the billing lines support on their own. Supported keeps the schedule figure wherever the invoices back it and drops to the invoice figure where they do not.

## Cohorts, revenue retained at 12 months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q4 | 41 | 85.0 | 89.0 |

## ARR bridge, three ways

Schedule is what the company reports. Invoices is what the billing lines show on their own. Supported keeps the schedule figure where the invoices back it. Difference is schedule minus supported. Figures are ARR (MRR times 12). Every movement traces to its accounts in bridge_accounts.csv.

### As of 2025-11

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 868,800 | 0 | 0 | 0 | 9,600 | 0 | 859,200 |
| invoices | 865,800 | 25,200 | 0 | 28,800 | 0 | 0 | 919,800 |
| supported | 834,000 | 0 | 0 | 0 | 0 | 0 | 834,000 |
| difference | 34,800 | 0 | 0 | 0 | 9,600 | 0 | 25,200 |

### Window 2024-12 to 2025-11, movements summed

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 909,600 | 96,000 | 0 | 7,200 | 14,400 | 139,200 | 859,200 |
| invoices | 878,400 | 84,600 | 0 | 84,000 | 4,800 | 122,400 | 919,800 |
| supported | 874,800 | 48,000 | 0 | 55,200 | 4,800 | 139,200 | 834,000 |
| difference | 34,800 | 48,000 | 0 | -48,000 | 9,600 | 0 | 25,200 |

The largest difference between the two bases over the window is in new: 48,000 ARR. The schedule and the invoices disagree most about that movement.

## Accounts to review first

| account | schedule MRR | invoice MRR | unresolved MRR | cause | months not supported |
|---|---:|---:|---:|---|---:|
| Silent Partner Inc | 2,100 | 0 | 2,100 | unmatched_schedule_only | 12 |
| Quiet Creek Software | 1,000 | 1,300 | 0 | under_stated | 12 |
| Granite Peak Software | 4,200 | 4,200 | 0 | over_stated | 11 |
| Orphan Billing LLC | 0 | 950 | 0 | unmatched_invoice_only | 10 |
| Juniper Ridge Labs | 8,000 | 8,000 | 0 | ramp_or_proration | 3 |
| Lantern Field Co | 0 | 1,400 | 0 | under_stated | 3 |
| Northwind Dynamics | 2,400 | 4,800 | 0 | timing | 2 |
| Cedar Loop Systems | 3,000 | 3,000 | 0 | credit_or_rebill | 1 |
| Nimbus Field Systems | 0 | 2,100 | 0 | unmatched_invoice_only | 1 |
## Deferred revenue implied by the invoices

Billed is the invoice line in the month it was raised. Recognised is the share the kit spreads into each month of the service period. The difference, carried forward, is deferred revenue where the billing runs ahead and unbilled revenue where the recognition does. **The two sides are reported apart and never netted**, because a book with money on both sides would otherwise read as nil.

| month | opening | billings | recognised | closing | of which deferred | of which unbilled |
|---|---:|---:|---:|---:|---:|---:|
| 2024-12 | 22,000 | 71,200 | 73,200 | 20,000 | 20,000 | 0 |
| 2025-01 | 20,000 | 75,200 | 77,200 | 18,000 | 18,000 | 0 |
| 2025-02 | 18,000 | 76,150 | 78,150 | 16,000 | 16,000 | 0 |
| 2025-03 | 16,000 | 76,150 | 78,150 | 14,000 | 14,000 | 0 |
| 2025-04 | 14,000 | 76,150 | 78,150 | 12,000 | 12,000 | 0 |
| 2025-05 | 12,000 | 76,150 | 78,150 | 10,000 | 10,000 | 0 |
| 2025-06 | 10,000 | 70,250 | 75,250 | 5,000 | 8,000 | 3,000 |
| 2025-07 | 5,000 | 73,150 | 72,150 | 6,000 | 6,000 | 0 |
| 2025-08 | 6,000 | 70,150 | 72,150 | 4,000 | 4,000 | 0 |
| 2025-09 | 4,000 | 70,150 | 72,150 | 2,000 | 2,000 | 0 |
| 2025-10 | 2,000 | 70,150 | 72,150 | 0 | 0 | 0 |
| 2025-11 | 0 | 98,650 | 76,650 | 22,000 | 22,000 | 0 |

Opening plus billings minus recognised equals closing in every month above; the kit asserts it and does not report these figures if it fails.

Journal for 2025-11: 1 lines, see journal.csv. Credited to deferred revenue 22,000, released from deferred revenue 0.

Deferred revenue implied by the invoices at 2025-11: 22,000. Per the general ledger: not provided.

This is a schedule a controller can post from, in `journal.csv`, with the accounts named in plain words. It is not a posting, not a chart of accounts and not an opinion on revenue recognition policy.

| account | closing deferred | closing unbilled | months of cover |
|---|---:|---:|---:|
| Copperline Freight | 22,000 | 0 | 11.0 |
| Blue Harbor Analytics | 0 | 0 |  |
| Granite Peak Software | 0 | 0 |  |
| Cedar Loop Systems | 0 | 0 |  |
| Northwind Dynamics | 0 | 0 |  |
| Juniper Ridge Labs | 0 | 0 |  |
| Maple Street Health | 0 | 0 |  |
| Lantern Field Co | 0 | 0 |  |
| Harbor Light Media | 0 | 0 |  |
| Quiet Creek Software | 0 | 0 |  |


## Matching

Exact id: 40. Normalised name: 1. Ambiguous: 0. Schedule only: 1. Invoices only: 2. Full table in match_table.csv.

## What the files cannot support

Invoice lines with no type the kit could classify: 0. Lines with no service period (spread to the invoice month instead): 15. Mapping warnings: 0.

The kit does not read contracts, order forms, the general ledger or bank records. Where the schedule and the invoices disagree, the kit shows the disagreement and the lines behind it. Which figure is right is a question for the company's finance lead, and in a transaction for the diligence team. Nothing here is an accounting opinion.

## Questions for finance

* Where are the invoices for the accounts with none?
* What caused each credit memo, and was the rebill for the same period?
* Which accounts carry schedule MRR above the invoices, and is there a contract or a billing gap behind each one?
* Do the first months bill below the schedule by contract (ramp) or by proration, and should the schedule show the ramp?
* Is invoice timing a month off by design (billing in arrears) or by accident?
* Which accounts bill above the schedule, and is the schedule stale or the billing wrong?
* Which billed accounts are missing from the schedule, and why?
