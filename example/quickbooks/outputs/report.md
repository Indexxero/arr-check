# Pilot findings, as of 2025-10

Inputs: schedule `schedule.csv` (203 rows), invoices `invoices.csv` (126 lines). Hashes in manifest.json. Kit 2026-10-25.

## Totals

| | ARR |
|---|---:|
| Reported on the schedule | 150,000 |
| Supported by invoices | 138,000 |
| Unresolved, needs review | 12,000 |
| Accounts on the schedule | 10 |
| Accounts with an exception in the last 12 months | 1 |

## Exceptions by cause

| cause | accounts | unresolved ARR |
|---|---:|---:|
| over_stated | 1 | 12,000 |

What each cause means: supported, the invoices back the schedule within tolerance. over_stated, the schedule carries more than the invoices show. under_stated, the invoices show more than the schedule. timing, the same money lands a month earlier or later. credit_or_rebill, a credit memo or rebill touched the month. duplicate_invoice, the same invoice id appears twice. ramp_or_proration, the first months bill below the schedule. classification, a non recurring or untyped line sits where recurring revenue is expected. unmatched_schedule_only, no invoices found for the account. unmatched_invoice_only, invoices with no account on the schedule.

## Retention, three ways

| basis | from | to | starting book MRR | accounts | GRR | NRR |
|---|---|---|---:|---:|---:|---:|
| schedule | 2024-10 | 2025-10 | 11,000 | 9 | 100.0 | 100.0 |
| invoices | 2024-10 | 2025-10 | 10,000 | 8 | 100.0 | 100.0 |
| supported | 2024-10 | 2025-10 | 10,000 | 8 | 100.0 | 100.0 |

Schedule is what the company reports. Invoices is what the billing lines support on their own. Supported keeps the schedule figure wherever the invoices back it and drops to the invoice figure where they do not.

## Cohorts, revenue retained at 12 months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q1 | 9 | 100.0 | 142.9 |

## ARR bridge, three ways

Schedule is what the company reports. Invoices is what the billing lines show on their own. Supported keeps the schedule figure where the invoices back it. Difference is schedule minus supported. Figures are ARR (MRR times 12). Every movement traces to its accounts in bridge_accounts.csv.

### As of 2025-10

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 150,000 | 0 | 0 | 0 | 0 | 0 | 150,000 |
| invoices | 138,000 | 0 | 0 | 0 | 0 | 0 | 138,000 |
| supported | 138,000 | 0 | 0 | 0 | 0 | 0 | 138,000 |
| difference | 12,000 | 0 | 0 | 0 | 0 | 0 | 12,000 |

### Window 2024-11 to 2025-10, movements summed

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 132,000 | 18,000 | 0 | 0 | 0 | 0 | 150,000 |
| invoices | 120,000 | 147,600 | 0 | 0 | 0 | 129,600 | 138,000 |
| supported | 120,000 | 30,000 | 0 | 0 | 0 | 12,000 | 138,000 |
| difference | 12,000 | -12,000 | 0 | 0 | 0 | -12,000 | 12,000 |

The largest difference between the two bases over the window is in new: 12,000 ARR. The schedule and the invoices disagree most about that movement.

## Accounts to review first

| account | schedule MRR | invoice MRR | unresolved MRR | cause | months not supported |
|---|---:|---:|---:|---|---:|
| Discount Co | 1,000 | 0 | 1,000 | over_stated | 12 |
## Deferred revenue implied by the invoices

Billed is the invoice line in the month it was raised. Recognised is the share the kit spreads into each month of the service period. The difference, carried forward, is deferred revenue where the billing runs ahead and unbilled revenue where the recognition does. **The two sides are reported apart and never netted**, because a book with money on both sides would otherwise read as nil.

| month | opening | billings | recognised | closing | of which deferred | of which unbilled |
|---|---:|---:|---:|---:|---:|---:|
| 2024-11 | 38,800 | 4,100 | 10,000 | 32,900 | 32,900 | 0 |
| 2024-12 | 32,900 | 4,100 | 10,000 | 27,000 | 27,000 | 0 |
| 2025-01 | 27,000 | 30,800 | 10,000 | 47,800 | 47,800 | 0 |
| 2025-02 | 47,800 | 4,100 | 10,000 | 41,900 | 41,900 | 0 |
| 2025-03 | 41,900 | 14,900 | 20,800 | 36,000 | 36,000 | 0 |
| 2025-04 | 36,000 | 6,800 | 10,000 | 32,800 | 32,800 | 0 |
| 2025-05 | 32,800 | 4,100 | 10,000 | 26,900 | 26,900 | 0 |
| 2025-06 | 26,900 | 22,100 | 11,500 | 37,500 | 37,500 | 0 |
| 2025-07 | 37,500 | 6,800 | 11,500 | 32,800 | 32,800 | 0 |
| 2025-08 | 32,800 | 4,100 | 11,500 | 25,400 | 25,400 | 0 |
| 2025-09 | 25,400 | 4,100 | 11,500 | 18,000 | 18,000 | 0 |
| 2025-10 | 18,000 | 42,800 | 11,500 | 49,300 | 49,300 | 0 |

Opening plus billings minus recognised equals closing in every month above; the kit asserts it and does not report these figures if it fails.

Journal for 2025-10: 4 lines, see journal.csv. Credited to deferred revenue 34,800, released from deferred revenue 3,500.

Deferred revenue implied by the invoices at 2025-10: 49,300. Per the general ledger: not provided.

This is a schedule a controller can post from, in `journal.csv`, with the accounts named in plain words. It is not a posting, not a chart of accounts and not an opinion on revenue recognition policy.

| account | closing deferred | closing unbilled | months of cover |
|---|---:|---:|---:|
| Annual Three | 33,000 | 0 | 11.0 |
| Annual Two | 10,500 | 0 | 7.0 |
| Annual One | 4,000 | 0 | 2.0 |
| Quarterly One | 1,800 | 0 | 2.0 |
| Discount Co | 0 | 0 |  |
| Monthly A | 0 | 0 |  |
| Monthly B | 0 | 0 |  |
| Monthly C | 0 | 0 |  |
| Monthly D | 0 | 0 |  |
| Monthly E | 0 | 0 |  |


## Matching

Exact id: 0. Normalised name: 10. Ambiguous: 0. Schedule only: 0. Invoices only: 0. Full table in match_table.csv.

## What the files cannot support

Invoice lines with no type the kit could classify: 0. Lines with no service period (spread to the invoice month instead): 113. Mapping warnings: 1.

The kit does not read contracts, order forms, the general ledger or bank records. Where the schedule and the invoices disagree, the kit shows the disagreement and the lines behind it. Which figure is right is a question for the company's finance lead, and in a transaction for the diligence team. Nothing here is an accounting opinion.

## Questions for finance

* Which accounts carry schedule MRR above the invoices, and is there a contract or a billing gap behind each one?
