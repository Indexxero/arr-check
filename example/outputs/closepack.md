# Revenue close pack, as of 2025-10

Inputs: `schedule.csv` (521 rows), `invoices.csv` (511 lines). Kit 2026-10-25. Every figure below is in a file beside this one; nothing here is an accounting opinion.

## 1. Reported against supported

| | ARR |
|---|---:|
| Reported on the schedule | 868,800 |
| Supported by invoices | 834,000 |
| Excluded from verified ARR | 34,800 |
| Accounts on the schedule | 37 |

## 2. ARR bridge, 2024-11 to 2025-10

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 909,600 | 96,000 | 0 | 7,200 | 4,800 | 139,200 | 868,800 |
| supported | 829,200 | 93,600 | 0 | 55,200 | 4,800 | 139,200 | 834,000 |
| difference | 80,400 | 2,400 | 0 | -48,000 | 0 | 0 | 34,800 |

## 3. Retention, three ways

| basis | GRR | NRR | starting book ARR | accounts |
|---|---:|---:|---:|---:|
| schedule | 84.2 | 85.0 | 909,600 | 41 |
| invoices | 84.7 | 84.7 | 832,800 | 38 |
| supported | 82.6 | 82.6 | 829,200 | 38 |

## 4. Cohorts, revenue retained at twelve months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q4 | 41 | 85.0 | 89.0 |

## 5. Concentration, supported basis

Top five accounts: 33.5 percent of supported ARR. Largest single account: Juniper Ridge Labs, 11.5 percent.

## 6. Exception register, 10 accounts, ten largest by unresolved ARR

| account | cause | unresolved ARR | months not supported |
|---|---|---:|---:|
| Silent Partner Inc | unmatched_schedule_only | 25,200 | 12 |
| Granite Peak Software | over_stated | 9,600 | 12 |
| Quiet Creek Software | under_stated | 0 | 12 |
| Orphan Billing LLC | unmatched_invoice_only | 0 | 9 |
| Juniper Ridge Labs | ramp_or_proration | 0 | 3 |
| Lantern Field Co | under_stated | 0 | 2 |
| Cedar Loop Systems | credit_or_rebill | 0 | 1 |
| Northwind Dynamics | timing | 0 | 1 |
| Maple Street Health | classification | 0 | 1 |
| Harbor Light Media | duplicate_invoice | 0 | 1 |

## 7. Deferred revenue implied by the invoices

At 2025-10: deferred 0, unbilled 0, reported apart.
Per the general ledger: 800. Difference: -800.

### ARR to recognised revenue, 2025-10

Monthly. Every row, with its accounts, in arr_to_revenue.csv.

| step | MRR |
|---|---:|
| recurring revenue on the schedule | 72,400.00 |
| less: unmatched_schedule_only | -2,100.00 |
| less: over_stated | -800.00 |
| **= supported by invoices** | **69,500.00** |
| plus: under_stated, schedule shows nothing | 1,400.00 |
| plus: unmatched_invoice_only | 950.00 |
| plus: under_stated, billed above the schedule | 300.00 |
| **= invoiced recurring, spread over service periods** | **72,150.00** |
| **= recognised revenue, deferred_rollforward.csv** | **72,150.00** |
| billed in the month, recurring and credit lines | 70,150.00 |
| plus: released from the net deferred balance (2,000.00 to 0.00) | 2,000.00 |
| **= recognised revenue, deferred_rollforward.csv** | **72,150.00** |
| one off lines in the month, outside ARR and outside the roll forward | 0.00 |

## 8. Since the previous run

First run, no comparison. Pass `--before <previous out folder>` next month.

## 9. The run that made this

Kit 2026-10-25. Schedule sha256 65e36e4953776f10, invoices sha256 0c50583d1cf5c1c0. Full hashes of every input and output in receipt.json; `python3 receipt.py verify` recomputes them.
