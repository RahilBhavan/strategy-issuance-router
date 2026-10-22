# Sources and coverage

Purpose: separate observed disclosures from scenario assumptions. Financial
source as-of: **2026-10-21**. Fetch timestamps are recorded separately in UTC.

The default fixture selects two weekly and twenty instrument rows (ten ATM and
ten buyback rows) from the versioned ledger CSV outputs. Only ATM rows enter this
router's capacity/comparison path. The full upstream ledger's broader corpus is
not needed for this demo. [Dependency](dependency.md) documents the public commit,
selection, exact artifact hashes and compatible external input contract.

Primary sources reopened during the publication review:

- [October 5 SEC 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526413164/mstr-20261005.htm): October 4 remaining capacity, in millions USD: MSTR 18,828.7, STRC 17,510.8, STRK 2,100.0, STRD 4,014.8, STRF 1,619.3. The router treats these as gross issuance ceilings by assumption.
- [October 19 SEC 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm): October 12–18 MSTR net proceeds $22.0M, preferred ATM proceeds zero. Net proceeds are after sales commissions. This filing is excluded from the October 9 decision.
- [Strategy proposal timeline and FAQ](https://www.strategy.com/it/mstr/vote): October 28 meeting, with new cadence conditional on approval. At the October 21 snapshot, this remains a proposal.

The selected source manifest retains the two filing-byte SHA-256 hashes and
`2026-10-22T00:55:06Z` fetch timestamps, corresponding to October 21 in Detroit.
The router does not reparse original HTML. The upstream reviewed build supplies
extraction provenance; selected CSV hashes separately establish artifact identity.
Fixture values were checked against the two primary tables; this does not audit
every historical upstream filing or guarantee corpus completeness.

All prices, yields, fees, limits, annual budget and mNAV in the scenario are
**synthetic assumptions**, not observed market data. A preferred security's legal
coupon is not its cash yield per gross financing dollar. Filing purchase prices
are period averages including fees, not decision-time market spot observations.
No rate, execution price, performance or treasury objective is inferred from
subsequent issuance. Third-party SEC/issuer material remains attributed to its
source and is not relicensed as project code.

## Comparison source review (2026-10-22)

Reopened the primary [October 5 SEC filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526413164/mstr-20261005.htm)
on 2026-10-22. Its October 4 table confirms MSTR $18,828.7M remaining capacity;
footnotes distinguish preferred face value (basis for dividends) from proceeds
net of sales commission. The table is capacity evidence, not a decision-time
preferred price/yield series. The BTC purchase table is a period aggregate
including expenses, not a point-in-time spot input. No fixture or hash changed.

Also reviewed Strategy's dated [July 31, 2025 results and capital framework](https://www.strategy.com/press/strategy-announces-second-quarter-2025-financial-results_07-31-2025)
on 2026-10-22. It defines issuer mNAV using enterprise value divided by Bitcoin
NAV and describes discretionary issuance thresholds. That definition reinforces
why this router's `gross/mnav` NAV-claim convention is a simplification, not a measured
common ownership dilution calculation or an implementation of issuer policy.
The older disclosure supplies no validated complete October 9, 2026 set of
execution prices, shares, preferred yields and mNAV. No observed market fixture
was added: the exact unresolved input is an attributed, internally consistent
point-in-time set for that decision date. Synthetic defaults remain explicit.
Optional price and share-count inputs enable arithmetic, not data certification.
