# Shared-assumption financing comparison

Scope accepted 2026-10-22. Baseline: clean `b35ff03`, 24 passing tests; no
repository glossary or decision directory exists. Existing spec/method govern.

Implement an opt-in JSON comparison (`--compare-financing`) between the existing
router, common-only, preferred-only and each enabled single preferred instrument.
Use the same decision date, target, fee, BTC price, yields, gross ticker limits,
annual dividend budget and pinned filing capacities. Preserve default CLI bytes.

Done conditions:

1. Each alternative exposes funded/unfilled net USD, fees, common NAV claim,
   annual preferred cash expense, proxy total and per-funded-dollar proxy cost.
   Incomplete funding never produces a full-target savings claim.
2. Capacity evidence and per-instrument constraint headroom are reported even for
   zero allocations; missing inputs remain explicit. No future actuals affect any
   alternative. Excluded instruments do not generate false missing-input errors.
3. Optional positive common price and pre-issue share count are accepted together;
   report new shares and new/(existing+new) ownership fraction, or null when
   unavailable. This is direct common ownership dilution, excluding conversion.
4. Tests prove hand-calculated metrics, constraints, missing inputs, dilution,
   partial-fill comparability, deterministic CLI and no-lookahead. Original 24
   tests, fixture hashes, default replay and figure checks continue to pass.
5. Document a five-minute offline example and source/reproduction limits; push
   scoped changes to existing main and inspect bounded CI status.

Non-goals: changing the allocation objective, historical backtests, legal issuance
feasibility, debt/cash alternatives without capacity inputs, settlement lots,
visual changes, paid feeds or modifications to the pinned ledger/schema.

Evidence review: primary SEC and issuer pages inspected 2026-10-22. A complete
independently validated point-in-time market set for the demo decision is not
available from these sources. Keep demo market inputs synthetic; do not substitute
coupon designations, period-average execution prices or stale share counts.
