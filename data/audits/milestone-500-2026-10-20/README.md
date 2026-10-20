# Milestone 500 — reviewed additions, 20 October 2026

The catalogue grows from 478 to 500 with 22 exact Eurostat source slices. No additional provider, scraping, derived synthetic observations or manually entered values are introduced. Every selected series has at least ten Greek observations and at least two observations in each default comparison period (2016–2018 and 2020–2022). All Greek series were checked against existing series for exact duplicates. This is not a claim that all 500 indicators are independent concepts or have full coverage for every government.

## Published additions

| Category | Indicators | Count |
| --- | --- | --- |
| Living standards & housing | Holiday affordability; child income poverty; depth of poverty; bottom-40% income share; median housing-cost burden; food, rent and electricity inflation | 8 |
| Jobs & earnings | Very low household work intensity; involuntary part-time work; long working hours; inactivity due to caring duties; fatal workplace accidents | 5 |
| Education & research | Under-3 formal childcare for 30+ hours; adult learning in the last four weeks; recent-graduate employment | 3 |
| Health & care | Bad/very bad self-rated health; long-standing illness; health-related activity limitations; preventable and treatable mortality under 75 | 5 |
| Transport & infrastructure | Passenger-transport services inflation | 1 |

Most end in 2025. Fatal workplace accidents end in 2024; both mortality series end in 2023. Source flags, missing years, source update times and retrieval hashes are retained. See receipt.json for exact API URLs and coverage. The existing weekly official-data workflow refreshes these slices.

## Definitions and overlap

- Child poverty is a useful under-18 breakdown of the existing overall poverty concept; do not sum the rates. Poverty depth measures a different question: how far the median poor person's income is below the poverty threshold.
- Low work intensity uses the EU 2030 (0–64) definition and overlaps with AROPE. No splice with the older 0–59 definition.
- Childcare selects only H_GE30 for under-3s. It is participation, not access, unmet demand, quality or affordability. It excludes shorter attendance and is not spliced with the newer 25-hour definition.
- Involuntary part-time work divides by part-time workers, not all workers. Caring-related inactivity uses PC_POP (all people aged 20–64), not the alternative denominator restricted to inactive people wanting work.
- Long working hours are usual 49+ hours in the main job, including self-employment. Existing ILO actual average hours answer a different question.
- Health survey indicators cover all people aged 16+ and are not age-standardised. Mortality indicators are age-standardised rates for causes considered preventable or treatable under 75; they do not identify individual avoidable deaths or establish government causality.
- Median housing-cost burden differs from the existing share above the 40% overburden threshold. Both costs and income are net of housing allowances.
- Inflation uses current prc_hicp_ainr / ECOICOP version 2, not discontinued prc_hicp_aind. Annual-average rates may be negative. Food CP01, rent CP041, electricity CP0451 and passenger services CP073 are components of general inflation, not rates to add. A government's mean annual inflation is not cumulative price growth; rental inflation excludes owner-occupied housing and property prices.

## Deferred and excluded

The exploratory screen covers 37 dataset routes (screen.json and screen-more.json). These are dataset checks, not 37 proposed independent KPIs. Four otherwise useful housing-condition indicators (damp/leaks, noise, local pollution, perceived local crime) have only one observation in 2020–2022 and were deferred rather than presented as strong period comparisons. Their API responses show gaps in 2021–2022; no values were filled in. prc_hpi_a lacks usable Greek coverage. Children's unmet medical needs are sparse modules. Duplicate SDG summaries of already-published unmet medical care and adult-learning concepts were excluded. The attempted sdg_04_30 and sdg_03_40 routes returned 404. Other unselected routes require further review.

## Validation

The 22 new raw responses were replayed with exact dimensions, flags and SHA-256 checks. The reader now fails closed when a filter is ignored or returns a different singleton code. Bounds allow valid negative inflation. Regression tests cover source replacement, denominators, default comparison coverage and negative values. Existing snapshot, calculation, multi-KPI comparison, export, landing and provider tests are run before publication. Full official-data refresh verifies all provider payloads after publication.

Official references:
- https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_ainr/default/table
- https://ec.europa.eu/eurostat/cache/metadata/en/prc_hicp_esms.htm
- https://ec.europa.eu/eurostat/databrowser/view/ilc_lvhl11n/default/table
- https://ec.europa.eu/eurostat/databrowser/view/hlth_cd_apr/default/table
- https://ec.europa.eu/eurostat/databrowser/view/lfsa_qoe_3a2/default/table
