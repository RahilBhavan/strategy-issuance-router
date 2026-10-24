# Verification and correctness review

Purpose: record executed checks, proven fixes and limits. Source snapshot: October
21, 2026. Initial baseline: commit `ff4688d`, clean tree, Python 3.14.7, 17 tests passed.

```bash
python -m unittest discover -s tests -v
python -m compileall -q router scripts tests
python -m router --scenario examples/synthetic.json
python scripts/render_result.py --check
```

Local result at the first review: **24 tests pass** (the current count is 45; see the reader-test model update below). Two independent CLI processes match each
other and `examples/result.json` byte for byte. CI repeats tests, compilation,
CLI result diff and generated-figure check, using pinned action SHAs, Python 3.14.0
and read-only repository permissions. There are no runtime third-party packages
or static typechecker dependencies; compileall checks Python syntax, not types.

## Fixed and proven

- `router/io.py`: weekly dates were unchecked. Replacing a target start with
  `2099-01-01` allowed a decision within its real reporting week. Chronology and
  duplicate-week checks now refuse the malformed ledger. Regression first failed,
  then passed.
- `router/io.py`: JSON decimal `9007199254740993.01` became
  `9007199254740994.0` through float conversion. Direct Decimal parsing preserves
  the literal. The exact-value regression first failed, then passed. Demo output
  was regenerated because preserving `.10` changes trailing zeros, not allocations.
- `router/io.py`: an instrument with a different start date still joined the target
  week's actual comparison. Import now validates its accession/period join and
  start, filing date and URL agreement. Regression first failed, then passed.
- `router/core.py`: yield `.14`, budget `2`, fee `0`, target `10000` and gross limit
  `10000` yielded a dividend of `2.000000000000000000000000001`. Conservative bound
  division removes the excess. Target `1`, fee `.1` previously reported constrained
  for residual `1E-28`; documented fill tolerance now classifies it filled while
  retaining the residual. Both regressions first failed, then passed.
- The mutable sibling dependency was removed. The default bundled ledger snapshot
  and its artifact hashes are exercised by tests. Only an explicit `--ledger` uses
  an external checkout.

- `router/__main__.py`: BTC price `1e-999999999` caused an unhandled Decimal
  arithmetic traceback. The CLI now returns error exit 2 with no result. The
  subprocess regression first failed, then passed. Extreme magnitudes remain
  unsupported, with a diagnostic rather than a successful recommendation.

## Review coverage

All seven code-reviewer dimensions were swept: correctness, error handling,
security, accessibility, performance, dead code and project conventions. No UI
exists; CLI diagnostics and figure text/alt descriptions were inspected. No
measured performance, dead-code or executable security defect survived verification.
A read-only independent T3 review confirmed the greedy ordering for the stated
fractional model and supplied the Decimal budget regression. Its task request ID
was `router-independent-review-1`; it did not edit files or certify security.

Other cases cover future-data independence, cutoff during target week, target
missing/ambiguous, missing yields/mNAV/capacity/actuals, nonfinite/negative/boolean
numbers, zero budgets/capacities, duplicate instruments, tie-breaking, and BTC
unit changes without USD allocation changes. No network retry or persistent write
path exists in this CLI; repeat runs are read-only and deterministic.

## Figure and source checks

The SVG table is generated from the committed result, checked for drift in CI and
visually rendered at 680px and phone width. It uses Rahil's light figure palette;
IBM Plex Sans is requested with a system sans-serif fallback, so typography varies
by host. No geometric financial encoding or market-performance chart is used.
Primary SEC capacity and actual tables were reopened during review. Market inputs
remain synthetic: no sufficiently complete attributed point-in-time mNAV/yield
scenario was assembled. Filing purchase prices are not substituted for decision-time
BTC spot. Daily-dividend approval remains conditional at the source snapshot.

Remote commit, fresh-clone and CI evidence are recorded in [publication](publication.md).

## Financing comparison slice (2026-10-22)

Baseline clean `b35ff03`: 24 tests pass. After the opt-in comparison: 33 tests pass.
Nine new tests cover hand-calculated fees/costs/dilution, partial-fill comparison
eligibility, shared budget/capacity/limits, missing inputs, null dilution, empty
policy, no-lookahead, validation and deterministic CLI compatibility. Default
replay, compileall, fixture hashes and generated SVG remain unchanged. See
[reproduction and measured limits](financing-comparison.md).

## Reader-test model update (2026-10-22)

Baseline clean `003710d`: 33 tests pass. After the update: **45 tests pass** on
Python 3.14.7. Existing tests were kept; fixtures that used STRK as a generic
preferred now use STRF, because STRK requires conversion inputs. Expected
allocations changed where the cost basis changed (router demo: MSTR then STRK).
New tests check each instrument's cost per net dollar against independent
formulas (including a Black–Scholes STRK conversion value written with
`statistics.NormalDist`), STRK reported missing without conversion inputs,
conversion cost rising with MSTR price and volatility, discount-rate break-even
and ranking flip, mNAV 0.95 warning and `block`, binding constraints, forward
weeks absent from the ledger, `--no-actuals`, display quantization, new field
validation, the `--check` pass line and actual-issuance independence.
