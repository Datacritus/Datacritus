# Everyday-life Eurostat additions — 20 October 2026

Four exact annual EU-SILC slices add distinct, practical questions to the catalogue. Live API payloads were fetched and decoded using the existing Eurostat reader; source status flags and SHA-256 receipts are retained. All six existing comparison geographies use the same slice. The receipt records each source URL, retrieval time, update time and Greek coverage. Refresh uses the existing weekly official-data workflow.

| Indicator | Dataset | Greek history | Category |
| --- | --- | --- | --- |
| Unable to meet unexpected expenses | ilc_mdes04 | 2003–2025, 23 observations | Living standards & housing |
| Unable to afford a protein-rich meal every other day | ilc_mdes03 | 2003–2025, 23 observations | Living standards & housing |
| Making ends meet with great difficulty | ilc_mdes09 | 2003–2025, 23 observations | Living standards & housing |
| Unmet dental needs: cost, distance or waiting | hlth_silc_09 | 2008–2025, 18 observations | Health & care |

The first three measure people in households, not a percentage of households. Household composition and poverty status are both TOTAL. Making ends meet selects only GRT (great difficulty); it does not combine all levels of difficulty. Dental care uses the entire population aged 16+, both sexes, all income quintiles, reason TXP_TFAR_WLIST. Never splice the different denominator in hlth_silc_09b.

These are related measures of hardship, not independent scores to add together. Food affordability and unexpected expenses overlap conceptually with material deprivation but answer specific questions not previously published as separate series. Dental needs are distinct from the existing medical examination series. No identical Greek series or exact source slice is duplicated. Survey breaks, estimation and other source flags remain visible; comparisons describe change during a government period, not causality.

Formal childcare (ilc_caindformal) was examined but deferred: the API separates zero, 1–29 and 30+ hours; participation must not be described as unmet demand, affordability or access. A reviewed aggregation and clear label are needed before publication. New 25-hour variants must not be spliced into the older series.

Validation: all 15 Eurostat selected series checked, including replay of the four new raw payloads; snapshot coverage/category checks; existing calculation, government comparison, infographic, landing and provider tests. Production full refresh replays all sources in CI.
