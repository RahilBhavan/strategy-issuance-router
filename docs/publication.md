# Publication receipt

Purpose: record the reviewed public source and reproducibility evidence.

Publication is in progress. The persistent T3 goal remains active until the remote
main commit, fresh remote clone and GitHub Actions run are verified. No deployment,
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

Final remote, clean-clone and CI evidence will be appended after verification.

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

Final receipt commit verification is recorded below.
