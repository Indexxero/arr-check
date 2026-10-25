# Revenue close pack, as of 2025-10

Inputs: `schedule.csv` (203 rows), `invoices.csv` (126 lines). Kit 2026-10-25. Every figure below is in a file beside this one; nothing here is an accounting opinion.

## 1. Reported against supported

| | ARR |
|---|---:|
| Reported on the schedule | 150,000 |
| Supported by invoices | 138,000 |
| Excluded from verified ARR | 12,000 |
| Accounts on the schedule | 10 |

## 2. ARR bridge, 2024-11 to 2025-10

| basis | start | new | reactivation | expansion | contraction | churn | end |
|---|---:|---:|---:|---:|---:|---:|---:|
| schedule | 132,000 | 18,000 | 0 | 0 | 0 | 0 | 150,000 |
| supported | 120,000 | 30,000 | 0 | 0 | 0 | 12,000 | 138,000 |
| difference | 12,000 | -12,000 | 0 | 0 | 0 | -12,000 | 12,000 |

## 3. Retention, three ways

| basis | GRR | NRR | starting book ARR | accounts |
|---|---:|---:|---:|---:|
| schedule | 100.0 | 100.0 | 132,000 | 9 |
| invoices | 100.0 | 100.0 | 120,000 | 8 |
| supported | 100.0 | 100.0 | 120,000 | 8 |

## 4. Cohorts, revenue retained at twelve months

| cohort | accounts | schedule | supported |
|---|---:|---:|---:|
| 2024Q1 | 9 | 100.0 | 142.9 |

## 5. Concentration, supported basis

Top five accounts: 75.7 percent of supported ARR. Largest single account: Annual Three, 26.1 percent.

## 6. Exception register, 1 accounts, ten largest by unresolved ARR

| account | cause | unresolved ARR | months not supported |
|---|---|---:|---:|
| Discount Co | over_stated | 12,000 | 12 |

## 7. Deferred revenue implied by the invoices

At 2025-10: deferred 49,300, unbilled 0, reported apart.
Per the general ledger: not provided.

## 8. Since the previous run

First run, no comparison. Pass `--before <previous out folder>` next month.

## 9. The run that made this

Kit 2026-10-25. Schedule sha256 4d1b25ddf0b0f898, invoices sha256 04350f0bb7ceffa1. Full hashes of every input and output in receipt.json; `python3 receipt.py verify` recomputes them.
