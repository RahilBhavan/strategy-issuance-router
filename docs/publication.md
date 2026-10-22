# Publication receipt

Purpose: record the reviewed public source and reproducibility evidence.

Reviewed source is published publicly. The source commit, fresh remote clone and
GitHub Actions run below have been verified. No deployment,
trade, account action or license selection is included.

## Prepublication review

- Started from `ff4688d`; preserved v1 implementation and main history.
- Baseline 17 tests; current 24 tests, including proven chronology, CSV join,
  JSON precision, binding-budget and negative CLI regressions.
- Inspected all reachable Git blobs and current files: no credential patterns,
  private data artifacts, databases, caches, embedded contact records or oversized
  blobs found. Largest original reachable blob: 7,936 bytes. Initial author
  metadata was confirmed already public on the author's GitHub; it is preserved.
- Only selected public SEC numeric records/URLs/hashes are bundled, with attribution.
- No code license chosen; no license file yet. No PR is used for the authorized
  initial public publication.

The evidence below records the initial source check and final reviewed dependency.

## Verified first public source

- Repository: https://github.com/RahilBhavan/strategy-issuance-router (public).
- Default branch `main`, verified source commit
  `4db2ba38c7d62a57c8c1d9a3f81454abed7b9d3e`.
- Fresh HTTPS clone in `~/scratch/strategy-issuance-router/remote-clone`: 24 tests
  pass, compileall succeeds, generated figure matches. Two fresh CLI processes
  match `examples/result.json` byte for byte.
- Demo SHA-256: `e456ecfb09a1520138894f6ba3de6a0dbfebc37223747adf7f175c55047cc108`.
- [GitHub CI run 39718670524](https://github.com/RahilBhavan/strategy-issuance-router/actions/runs/39718670524)
  passed all steps on Python 3.14.0.
- Bundled rows/full upstream artifact hashes also match a clean committed ledger
  checkout at `3c95b9e061876907ebefc7e3153f72d0b2e205bf` after `python -m ledger restore`.

## Reviewed public dependency pin

The ledger owner published reviewed source commit
`94c70044aaf14eea2ffb53deffd1a1f36bdec52e` with stable schema 1.0.0. This router now
pins that SHA and `data/contract.json` hash. Its normalized CSV artifacts and
selected rows are unchanged. Fetched that exact public SHA into an isolated
checkout, restored CSVs, and verified commit, contract, upstream hashes, selected
rows and original source-manifest entries. All match; no fixture value changed.

## Final reviewed source verification

- Verified source commit: `be614b9ddfacb98ae510dd46310a991e40cd3591` on remote
  default branch `main`.
- [GitHub CI run 39718855863](https://github.com/RahilBhavan/strategy-issuance-router/actions/runs/39718855863)
  passed all steps using pinned checkout v7.0.1/setup-python v7.1.0 actions and
  Python 3.14.0. No Node deprecation annotation remained.
- A new HTTPS clone of that source commit passed 24 tests, compileall, figure
  generation check and the upstream dependency verification command. Two fresh
  CLI processes matched the committed demo, SHA-256 unchanged from above.
- The receipt-only follow-up commit records these completed checks. Its exact SHA
  and final branch CI status are reported in the delivery message, avoiding a
  self-referential commit hash inside this file.

## Remaining limits

Synthetic market assumptions; scenario replay rather than historical backtest.
Common NAV claim versus one-year preferred cash expense remains asymmetric.
No liquidity, full principal/conversion valuation or legal issuance feasibility
model. Source hashes prove identity, not completeness, certification or investment
suitability. No license file yet. October 28 dividend vote remains pending at the
October 21 source snapshot. See method and sources for details.

## Update 2026-10-22: license

The MIT license was added in `LICENSE`. It covers this project's code only. Earlier statements in this record that no license file existed describe the state at publication.

## Update 2026-10-22: reader-test model fixes

A cold-reader test found that the CLI required the target week's 8-K and that the one-year proxy favored preferreds. The router now values all instruments as present value of claims per net dollar (capitalized preferred dividends, STRK conversion value, common NAV claim), warns or blocks common below mNAV 1, supports forward weeks without actuals, and rounds output for display. The October 12–18 replay changed from $3.11M to $24.875M of common; see [method](method.md). Hosted CI for the pushed commit is the verification record.
