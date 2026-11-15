# data.gov.gr qualification audit — 15 November 2026

## Decision

**21 distinct indicators qualify for a controlled import. The catalogue would grow from 500 to 521 if all are implemented. No production indicators have been added.**

This is a conservative evidence-backed admission count, not a claim that 21 is the maximum possible yield of the portal. All 23,205 catalogue records were screened at metadata level. The numeric audit downloaded and parsed 53 Bank of Greece workbooks. The 21 qualifying fields come from 12 datasets; every one of those 12 resources was fetched again with HTTP 200 and identical SHA-256. Unexamined or uncertain resources contribute zero to the count.

## Qualification rules

- A specific licence and identifiable producer; selected sources carry CC BY 4.0 catalogue metadata.
- Directly retrievable, successfully parsed observations; no fabricated or inferred missing values.
- A distinct national question beyond existing metric definitions, not a new language, region, frequency or another source for the same concept.
- At least five complete calendar years and a complete observation year of 2024 or later. Selected histories actually contain 6–25 complete years.
- Explicit units, scope, aggregation rules and source revision caveats.
- A repeatable retrieval approach through catalogue resource metadata, preserving a last valid snapshot when unavailable. Two immediate successful fetches establish present reproducibility, not long-term uptime.

## Qualified series

| # | Indicator | Group | Native coverage used | Complete annual years | Annual rule |
|---|---|---|---|---|---|
| 1 | Apartment prices — national index | Housing | 2006–2025 (quarterly) | 2006–2024 | mean |
| 2 | Household deposit interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 3 | Household term deposits up to one year — interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 4 | Consumer loan interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 5 | Housing loan interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 6 | Non-financial business loan interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 7 | Sole-proprietor loan interest rate | Interest rates | 2015–2025 (monthly) | 2015–2024 | mean |
| 8 | Loans to non-financial corporations — outstanding | Lending | 2019–2025 (monthly) | 2019–2024 | year_end |
| 9 | Housing loans to individuals and NPISH — outstanding | Lending | 2019–2025 (monthly) | 2019–2024 | year_end |
| 10 | Consumer loans to individuals and NPISH — outstanding | Lending | 2019–2025 (monthly) | 2019–2024 | year_end |
| 11 | Non-financial corporation deposits and repos — outstanding | Deposits | 2019–2025 (monthly) | 2019–2024 | year_end |
| 12 | Household and NPISH deposits and repos — outstanding | Deposits | 2019–2025 (monthly) | 2019–2024 | year_end |
| 13 | Gross external debt — all sectors | External position | 2004–2025 (quarterly) | 2004–2024 | year_end |
| 14 | Net international investment position | External position | 2004–2025 (quarterly) | 2004–2024 | year_end |
| 15 | Balance of trade in goods — balance-of-payments basis | External trade | 2002–2025 (monthly) | 2002–2024 | sum |
| 16 | Balance of services — balance-of-payments basis | External trade | 2002–2025 (monthly) | 2002–2024 | sum |
| 17 | Inbound visitor average stay | Tourism | 2013–2024 (annual) | 2013–2024 | published |
| 18 | Inbound visitor expenditure per trip | Tourism | 2013–2024 (annual) | 2013–2024 | published |
| 19 | Inbound visitor expenditure per overnight stay | Tourism | 2013–2024 (annual) | 2013–2024 | published |
| 20 | Nominal effective exchange rate — broad index | Competitiveness | 2000–2025 (monthly) | 2000–2024 | mean |
| 21 | Real effective exchange rate — broad CPI-based index | Competitiveness | 2000–2025 (quarterly) | 2000–2024 | mean |

## Overlap and exclusions

The current 500-metric snapshot was checked for existing definitions, not only exact codes. Current-account balance (BN.CAB.XOKA.GD.ZS), total domestic private credit (FS.AST.PRVT.GD.ZS), tourism arrivals/receipts, public debt and government interest expenditure are not counted again. NFC loans, housing loans and consumer loans answer distinct borrower/product questions; loan interest rates are different from economy-wide short/long market rates. Gross external debt includes all sectors and is different from general-government debt.

Regional apartment/commercial-property series are not counted as additional national indicators. Commercial retail/office rents must never be relabelled residential rents. Country-of-origin tourism splits and FDI industry/country dimensions are not counted individually. Specialist monetary balance-sheet lines, gold quotes and a library inventory are outside this admission recommendation. Payments statistics inspected end in 2023 and are held for freshness/definition work. Registered-unemployment and electricity CSVs were reachable but licence and coverage have not been established, so neither is admitted.

## Full-catalogue screening disposition

These categories are triage outcomes, not manual verification of every resource. The order of classification matters: map layers/stations are classified by scope before licence.
- outside_current_national_indicator_scope: 12,115
- hold_restrictive_terms: 944
- hold_licence_not_established: 7,300
- not_qualified_for_current_count: 1,424
- hold_no_direct_tabular_resource: 1,369
- examined_not_selected: 41
- qualified_source: 12

## Import conditions

Retain provisional flags; do not mix complete annual data with year-to-date data. Use year-end stocks, sums of complete monthly flows, and clearly labelled time averages of monthly rates/indices. Use the published annual tourism TOTAL, not averages of country means. Preserve NPISH and institutional scope. Restrict rates to 2015 onward and tourism to 2013 onward as documented in the manifest. The lending/deposit histories begin in 2019 and do not support arbitrary comparisons with earlier governments.

The housing source index is 2007=100, independently checked against its 2007 quarterly mean. NEER/REER use the producer-documented 2000=100 basis. The exchange-rate rise represents appreciation or reduced price competitiveness according to the source; higher is not automatically better.

## Evidence

- qualified-series.json: exact source fields, resource IDs, original URLs, hashes, numerical coverage, extracted annual values and notes.
- resource-receipts.json: all 53 parsed workbook receipts and 12 repeat downloads.
- qualify.py: reproducible numerical qualification logic used for the selected fields.

## Remaining uncertainty

Licence absence in metadata is not proof reuse is forbidden. Other records remain unqualified until their rights, actual observation coverage and unique value are established. This audit does not certify the entire portal or every workbook column as ready for publication.
