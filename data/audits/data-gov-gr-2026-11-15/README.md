# data.gov.gr catalogue audit — 2026-11-15

## Scope and evidence
Enumerated all 23,205 catalogue records through CKAN package_search (24 pages, sorted by ID); unique IDs verified. Compared initial candidate themes with the current 500-metric Datacritus snapshot. This is a complete metadata inventory, not a claim that every underlying resource has been downloaded or validated.

Catalogue contains 109,838 resource entries (not unique indicators); 1,274 datasets advertise at least one active DataStore resource. Licence metadata is missing on 15,776 records and explicitly unspecified on another 3,544. Those counts flag review needs, not a legal conclusion that reuse is forbidden.

## Strong additions to investigate
- Bank of Greece apartment price indices, including geographical breakdowns.
- Deposit and loan interest rates.
- Credit volumes, flows and growth.
- Deposit balances and flows.
- Monthly balance of payments and travel-account details.
- Registered unemployment and unemployment-benefit recipients (different concept from survey unemployment).
- Industrial producer-price series.
- Electricity consumption and regional energy series.
- Business-register, education, healthcare and regional series where sufficiently continuous.

Bank of Greece records examined carry CC BY 4.0 metadata. Existing Datacritus title screening found no direct apartment-price, loan/deposit interest-rate, registered-unemployment or industrial-producer-price metric; this is preliminary semantic screening rather than a definitive deduplication verdict.

## Actual resource probes
- oaed_unemployment CSV: HTTP 200; columns asofdate, unemployed, benefits; first sample begins February 2010. Licence absent in catalogue. Full date range and revisions not yet verified.
- electricity_consumption CSV: HTTP 200; columns area, date, energy_mwh; sample includes island observations in August 2020. Licence absent in catalogue. Do not assume national coverage or current freshness.
- Bank of Greece apartment prices by geographical area: HTTP 200; genuine XLS file signature; CC BY 4.0 catalogue metadata. Workbook coverage and units still require parsing.

## Integration gates
Verify actual observation dates (not metadata_modified), definition, geographic coverage, frequency, units, historical breaks, licence/attribution, update reliability, and overlap with current sources. Prefer the original producer endpoint when the portal merely catalogues it. Do not merge registered unemployment with survey unemployment, commercial rents with household rents, or regional consumption with national totals.

No production indicators added.
