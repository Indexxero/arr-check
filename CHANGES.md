# Changes to the kit

2026-10-05: first version, written and tested on fictional data only.

2026-10-22: stress test on five export shapes (Stripe plus HubSpot, Chargebee, QuickBooks plus a wide Excel schedule, Maxio with resellers, 3,000 customer scale). Changes forced by it: Excel input (.xlsx); wide schedules (one column per month) melted automatically; exact duplicate schedule rows dropped with a note, duplicate invoice rows kept and flagged; fuzzy customer name match (ratio 0.88 or above, marked for review); a credit column inside the invoice row ("Credits Applied") treated as a credit line; more than one currency raises a note, no conversion; --profile stops after the profile; date and amount parsing vectorised (66,000 rows: 297 s to 57 s). Not handled on purpose: reseller parent and child roll up (recorded, not rolled up), currency conversion, invoices with no service period are placed in their invoice month and flagged.
