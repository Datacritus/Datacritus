# AMECO connector and first reviewed release — 19 October 2026

The reusable provider connector reads the entire official 18-file CSV archive. The source inventory contains 793 Greek rows / 425 variable codes; these are not counts of independent or net-new KPIs. Publication is controlled by a reviewed manifest of exact dimensions, source title, source unit and category. Adding further approved families does not require another provider adapter.

## Release and access

- Provider: European Commission, Directorate-General for Economic and Financial Affairs (DG ECFIN).
- Version: Spring 2026, 3 June 2026 revision.
- Official source: https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database_en
- Download/API guide: https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database/bulk-downloads-and-api-access_en
- Exact archive URL and SHA-256 are recorded in scripts/ameco_selection.json. A different archive requires review; it cannot silently replace the approved release.
- The API responded during evaluation, but query-string dimension filters did not restrict the returned population dataset. The connector therefore uses the official complete CSV archive with exact client-side slice matching.
- Source CSV uses Windows-1252 for most chapters and UTF-8 for chapter 17. Decoding is explicit; no characters are silently discarded.

## Forecast policy

Only 1974–2024 is published from this release. The 2025–2027 window is excluded conservatively. This does not imply every earlier number is a directly observed final statistic: historical estimates, revisions, linked accounting standards and model-based quantities remain possible. The source CSV does not provide a forecast flag per observation. Structural fiscal balance is explicitly labelled as a Commission model estimate, with a derived MODEL_ESTIMATE flag. No confidence interval is invented.

The release/cutoff is intentionally pinned. Weekly refreshes re-fetch and validate that approved release; switching to the November release or admitting later years requires another metadata/forecast review. This preserves comparison integrity rather than treating forecasts as realised government outcomes.

## First published selection

Fourteen additions bring the catalogue from 460 to 474 series. They include linked breakdowns, not fourteen unrelated headline concepts:

- Core HICP price index (not annual inflation).
- Real compensation per employee (not take-home salary).
- Real unit labour costs, economy-wide and manufacturing (a sector breakdown).
- Household gross saving rate.
- Government implicit debt interest rate.
- Nominal short- and long-term interest rates (financial context, including euro-area monetary policy).
- Terms-of-trade impact on real income.
- Capital/output ratio.
- Structural government budget balance (model-dependent; not the headline deficit).
- General-government indirect taxes, direct taxes and net social contributions (revenue components; no summing with parent totals).

GDP levels/growth, population, headline unemployment and debt are excluded from this first selection to avoid duplicating existing headline series. Different price bases, currencies or index variants are not imported indiscriminately. Two existing labour-cost views share a family label, and tax components are labelled as components. Every selected Greek slice has at least 15 non-null years through 2024; the first batch has 520 Greek observations. Other five-country slots retain their exact source observations; EU aggregates are left unavailable rather than mapped to a potentially different EU composition.

## Provenance and reuse

Each metric retains the original variable, four-part slice, CSV chapter, source title/unit, reviewed bilingual context, source version/date, archive hash, receipt hash and original values. No interpolation, rescaling or currency conversion is performed. The archive is not duplicated in git: it is downloadable from the recorded official URL; refresh receipts and the raw archive are retained in data/raw during ingestion.

Reuse basis: the European Commission's default CC BY 4.0 notice for EU-owned content, subject to any individual/third-party exceptions. Source credit and the applied historical window accompany exports; no EU logo or endorsement is claimed. https://commission.europa.eu/legal-notice_en

## Checks

- Archive hash/shape, exact dimensions, expected source title and unit.
- Duplicate selection/rows, invalid numbers, null and zero preservation.
- Forecast-year exclusion and receipt mismatch rejection.
- Live download matched the pinned source archive and selected values.
- Complete comparison and infographic export suite, Greek and English, both layouts.
- Full refresh remains atomic: a failed provider cannot replace the published data snapshot.

The remaining catalogue entries are inventoried candidates, not approved publications. The next expansion should review additional AMECO families and avoid counting alternate units and transformations as new concepts.
