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
