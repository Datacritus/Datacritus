# Datacritus: grow beyond 419 reviewed indicators

The 3 October scan tested all 1,498 current World Bank WDI catalogue codes for Greece, Spain and Portugal, reconciled the 1,496-code upload, and refreshed 42 exact Eurostat extracts. Its 814 strong-coverage candidates include age, sex, unit and other variants. Before the October 2026 provider expansion, the site published 156 reviewed headline indicators, including 48 selected from that expansion audit. The 814 count predates those 48 integrations; it is not 814 additional candidates remaining today. It is not a validated count of independent KPI concepts.

## Recommended next implementation

1. Introduce metric families and a searchable detailed catalogue. Keep a curated headline selection in each of the 12 categories. Put meaningful age, sex, sector and region breakdowns under their parent measure. Count headline KPIs and detailed series separately; adding countries does not create new KPI concepts.
2. Replace the single embedded data snapshot with a small catalogue manifest and separate data files fetched when a metric is selected. Keep the current featured series available initially, cache requested series, and preserve share links and export behaviour. This prevents a thousand-series catalogue from forcing every visitor to download every observation.
3. Import the remaining World Bank candidates in reviewed thematic batches. Prefer interpretable definitions and current Greek coverage; discard currency variants that tell the same story. Recheck each selected identifier, provider licence, units, source vintage, flags, comparability and coverage before publication.
4. Expand exact Eurostat dimensions: employment by sex/age, sectors and regions; household income/housing by household group; education by age/sex; government spending by function; energy by source. Validate each extracted slice. Include subnational data only with explicit geography and consistent regional boundaries. These are additional detailed series, rather than unrelated headline KPIs.
5. Add specialist provider adapters only after exact Greek-series testing. AMECO macroeconomic data, UNESCO education data and ILO labour data are promising next routes. OECD/IMF/WHO/UN routes need series-specific validation. ELSTAT museum and other specialist releases can use reproducible file ingestion when an API is unavailable, retaining the original file, release date, checksum, extraction method and definition. An API documented in the research report does not by itself approve a Greek series for integration.

## Publication contract

Each series needs a stable identifier; parent family; primary category; bilingual title and interpretation; provider and dataset; exact dimensions; unit and change unit; geographical scope; source URL and API/file request; source/retrieval dates; version/checksum; original observations and flags; Greek and peer coverage; applicable reuse terms; and an explicit publication decision.

Duplicate detection uses provider, dataset, exact dimensions and units, with editorial checks for equivalent concepts across providers. A rate and its population denominator must remain explicit. National totals and their overlapping subgroups must never be summed accidentally. Methodology changes, missing years and stale series remain visible. Conditional, restricted and ambiguous data stays out of the published comparison tool.

## Scale target

Work toward **1,000+ validated detailed series**, with a much smaller curated headline layer. This is an engineering and editorial target, not a claim that 1,000 suitable Greek series have already passed validation. The confirmed audit pool is the starting point; additional Eurostat dimensions and specialist sources need further checks. Expand category depth according to available evidence rather than forcing equal counts in every category.

The next concrete deliverable should be the family catalogue and on-demand data loading, followed by the next validated batch. The government comparison tool will then consume that same catalogue without a separate manual import.

## October 2026 implementation

The 263 vetted additions (V-Dem 207, UIS 24, PWT 18, UNDP 14) expand the site from 156 to 419 reviewed definitions. The 140 named conditional candidates are excluded. The 23,670-entry inventory is not a distinct-KPI count. Source-based groups keep the larger catalogue navigable. Composites and components are related; the product does not combine them into politician rankings.
