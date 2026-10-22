# Versioned ledger contract

Purpose: reproduce the offline demo without a sibling checkout or network access.

Reviewed public ledger pin: [`94c70044aaf14eea2ffb53deffd1a1f36bdec52e`](https://github.com/RahilBhavan/strategy-8k-ledger/tree/94c70044aaf14eea2ffb53deffd1a1f36bdec52e), schema **1.0.0**. Its `data/contract.json` hash is also pinned.

The default CLI reads `fixtures/ledger-v1/data/weekly.csv` and `instrument_weekly.csv`.
These are selected public SEC-derived rows from the ledger's v1 CSV contract, not a
copy of its implementation. `provenance.json` pins the upstream repository/commit,
full upstream CSV hashes, selected artifact hashes and row counts. The selected
source manifest retains original HTML hashes and UTC fetch dates. A source as-of
of October 21, 2026 is separate from fetch times on October 22 UTC (October 21 in
America/Detroit). Hashes establish identity, not correctness or completeness.

Selection: all rows with `period_end` equal to `2026-10-04` or `2026-10-18`.
This is enough for the documented October 9 decision and October 18 evaluation.
It is not a full historical capacity service. For another scenario, pass a complete
compatible ledger root with `--ledger PATH`; do not interpret the small default
snapshot as complete coverage for arbitrary dates.

To reproduce from the pinned public ledger commit in `provenance.json`:

```bash
mkdir -p ~/scratch/strategy-issuance-router
git clone https://github.com/RahilBhavan/strategy-8k-ledger.git ~/scratch/strategy-issuance-router/ledger
# From the router checkout:
git -C ~/scratch/strategy-issuance-router/ledger checkout --detach 94c70044aaf14eea2ffb53deffd1a1f36bdec52e
(cd ~/scratch/strategy-issuance-router/ledger && python -m ledger restore)
python scripts/verify_dependency.py ~/scratch/strategy-issuance-router/ledger
```

Required weekly columns: `accession`, `filed`, `period_start`, `period_end`, `doc_url`.
Required instrument columns: these five plus `ticker`, `action`, `program`,
`currency`, `available_usd`, `amount_usd`. Additional v1 columns are retained and
ignored by the router. Money is USD, blank means missing, zero means stated zero.
Instrument rows must join their weekly row by accession and period end, with the
same start, filing date and document URL. Dates and chronology are validated;
duplicate weekly period ends or instrument identities are refused.

No ledger code is vendored or relicensed. The numerical records are attributed to
Strategy SEC filings; SEC documents and issuer material retain their own terms.
No private account, contact or identity data is included. The ledger owner retains
schema authority; upgrades require reviewing the pin, CSV hashes, selected rows,
regression tests and scenario output together.
