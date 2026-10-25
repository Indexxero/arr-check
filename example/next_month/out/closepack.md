# Revenue close pack, as of 2025-11

Inputs: `schedule.csv` (558 rows), `invoices.csv` (549 lines). Kit 2026-10-25. Every figure below is in a file beside this one; nothing here is an accounting opinion.

## 1. Reported against supported

| | ARR |
|---|---:|
| Reported on the schedule | 859,200 |
| Supported by invoices | 834,000 |
| Excluded from verified ARR | 25,200 |
| Accounts on the schedule | 37 |

## 2. ARR bridge, 2024-12 to 2025-11

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 909,600 | 96,000 | 0 | 7,200 | 14,400 | 139,200 | 859,200 |
| supported | 874,800 | 48,000 | 0 | 55,200 | 4,800 | 139,200 | 834,000 |
| difference | 34,800 | 48,000 | 0 | -48,000 | 9,600 | 0 | 25,200 |

## 3. Retention, three ways

| basis | GRR | NRR | starting book ARR | accounts |
|---|---:|---:|---:|---:|
| schedule | 83.1 | 83.9 | 909,600 | 41 |
| invoices | 85.5 | 89.6 | 878,400 | 40 |
| supported | 83.5 | 84.4 | 874,800 | 40 |

## 4. Cohorts, revenue retained at twelve months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q4 | 41 | 85.0 | 89.0 |

## 5. Concentration, supported basis

Top five accounts: 33.5 percent of supported ARR. Largest single account: Juniper Ridge Labs, 11.5 percent.

## 6. Exception register, 9 accounts, ten largest by unresolved ARR

| account | cause | unresolved ARR | months not supported |
|---|---|---:|---:|
| Silent Partner Inc | unmatched_schedule_only | 25,200 | 12 |
| Quiet Creek Software | under_stated | 0 | 12 |
| Granite Peak Software | over_stated | 0 | 11 |
| Orphan Billing LLC | unmatched_invoice_only | 0 | 10 |
| Juniper Ridge Labs | ramp_or_proration | 0 | 3 |
| Lantern Field Co | under_stated | 0 | 3 |
| Northwind Dynamics | timing | 0 | 2 |
| Cedar Loop Systems | credit_or_rebill | 0 | 1 |
| Nimbus Field Systems | unmatched_invoice_only | 0 | 1 |

## 7. Deferred revenue implied by the invoices

At 2025-11: deferred 22,000, unbilled 0, reported apart.
Per the general ledger: not provided.

## 8. Since the previous run

Before: `example/outputs`. New 1, changed 1, persisted 7, resolved 2.
Largest new: Nimbus Field Systems (0 ARR).
Largest resolved: Maple Street Health (0 ARR); Harbor Light Media (0 ARR).

## 9. The run that made this

Kit 2026-10-25. Schedule sha256 5a384b772c2431a1, invoices sha256 631ef547e0f16ed2. Full hashes of every input and output in receipt.json; `python3 receipt.py verify` recomputes them.
