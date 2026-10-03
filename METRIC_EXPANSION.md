# Audited metric expansion — 27 September 2026

This release adds the first 24 approved research requests to the existing 59 indicators: 83 total. The additional data comes from 21 World Bank series and three Eurostat series. All six existing country/EU slots are retained; unavailable observations remain null.

## Research crosswalk

| Research item | Requested indicator | Integration |
| --- | --- | --- |
| 7 | Consumer price index (2022) | FP.CPI.TOTL |
| 10 | Exports of goods and services (2022) | NE.EXP.GNFS.CD |
| 22 | Gross enrolment ratio in primary education (2021) | SE.PRM.ENRR |
| 26 | Primary school completion rate (2024) | SE.PRM.CMPT.ZS |
| 27 | Lower-secondary completion rate (2024) | SE.SEC.CMPT.LO.ZS |
| 30 | Share of primary school teachers who are women (2021) | SE.PRM.TCHR.FE.ZS |
| 36 | Forest area (2020) | AG.LND.FRST.K2 |
| 38 | Share of land area used for agriculture (2021) | AG.LND.AGRI.ZS |
| 39 | Freshwater withdrawals (2020) | ER.H2O.FWTL.K3 |
| 44 | Passenger-kilometers by rail (2021) | IS.RRS.PASG.KM |
| 46 | Tonne-kilometers of air freight (2021) | IS.AIR.GOOD.MT.K1 |
| 55 | Police officers per 1,000 people (2015) | ESTAT.POLICE.DENSITY (source rate / 100) |
| 59 | Share of population using at least a basic drinking water source (2022) | SH.H2O.BASW.ZS |
| 63 | Foreign direct investment, net outflows as share of GDP (2022) | BM.KLT.DINV.WD.GD.ZS |
| 66 | Annual scholarly publications in scientific/tech journals (2020) | IP.JRN.ARTC.SC |
| 68 | GDP per employed person (2022) | SL.GDP.PCAP.EM.KD |
| 122 | Population density (2025) | EN.POP.DNST |
| 123 | Birth rate (UN, 2023) | SP.DYN.CBRT.IN |
| 124 | Crude death rate (2023) | SP.DYN.CDRT.IN |
| 126 | Old-age dependency ratio (2023) | SP.POP.DPND.OL |
| 127 | Youth dependency ratio (2023) | SP.POP.DPND.YG |
| 129 | Share of population that is female (2022) | SP.POP.TOTL.FE.ZS |
| 130 | Average age of mothers at childbirth (2023) | ESTAT.MOTHERS.AGE |
| 135 | Government spending as a share of GDP (2022) | ESTAT.GOV.EXPENDITURE |

## Definitions and interpretation

- Police density is officers per 1,000 residents; raw Eurostat observations are per 100,000. Nulls and quality flags are preserved. Changes use absolute units, not percentage points.
- Mean maternal age covers all births, not only first births.
- Government expenditure is the general-government total (S13 / TE), not central-government expense.
- Export amounts use current US dollars and differ from the existing exports/GDP ratio. Forest area in km² differs from the existing land share.
- Rail passenger-km and air-freight tonne-km measure transport work, not passenger or cargo counts.
- Dependency ratios are demographic age ratios, not economic employment dependency. Gross education ratios can exceed 100%.
- New indicators have Greek labels and reading definitions. The original World Bank definition and source metadata remain in the snapshot.
- Country comparisons still require a common observed year. No missing-year interpolation or causal government score is introduced.

## Validation

The refresh pipeline fetches provider metadata and observations, then checks every retained value against its raw response. Data checks also cover the police-unit conversion, null/zero preservation and absolute versus percentage-point change units. Existing calculation and infographic checks cover the entire expanded catalogue in Greek and English, landscape and portrait.

The completed research audit contained 210 requests, not 210 unique deployable indicators. Conditional, unavailable and duplicate items are outside this release. The larger logo, 20px base type, strong buttons and infographic Studio already existed and are preserved.

## Second batch — 25 additional series

This batch expands 83 to 108 metrics, fulfilling 24 more research requests (GDP nominal and PPP are separate series for item 3). All additions use the existing automatic World Bank/Eurostat refresh, source checksums and quality flags. Sparse observations remain gaps.

| Research item | Series | Indicator |
| --- | --- | --- |
| 3 | NY.GDP.MKTP.CD | GDP, current prices |
| 3 | NY.GDP.MKTP.PP.CD | GDP at purchasing power parity |
| 76 | SH.ALC.PCAP.LI | Alcohol consumption, ages 15+ |
| 94 | SH.STA.ODFC.ZS | Open defecation |
| 96 | SH.STA.BASS.UR.ZS | Basic sanitation, urban population |
| 97 | SH.H2O.BASW.RU.ZS | Basic drinking water, rural population |
| 99 | SP.URB.TOTL.IN.ZS | Urban population share |
| 109 | SM.POP.RHCR.EA | Refugees hosted, UNHCR mandate |
| 116 | IT.MLT.MAIN.P2 | Fixed telephone subscriptions |
| 118 | FB.ATM.TOTL.P5 | ATM availability |
| 128 | SM.POP.TOTL | International migrant stock |
| 134 | GC.REV.XGRT.GD.ZS | Government revenue excluding grants |
| 140 | DC.ODA.TLDC.CD | Development aid to least developed countries |
| 142 | SP.POP.SCIE.RD.P6 | Researchers per million people |
| 162 | EG.EGY.PRIM.PP.KD | Primary energy intensity |
| 192 | DC.ODA.TOTL.CD | Net development aid provided |
| 200 | FI.RES.TOTL.MO | Reserves in months of imports |
| 40 | ESTAT.WASTE.RECYCLING | Municipal waste recycling rate |
| 81 | ESTAT.HOTELS.NONRESIDENT | Non-resident arrivals at hotels |
| 82 | ESTAT.HOTELS.RESIDENT | Resident arrivals at hotels |
| 85 | ESTAT.TOUR.TRIPS | Resident overnight tourist trips, domestic and abroad |
| 71 | ESTAT.LIFE.SATISFACTION | Overall life satisfaction, ages 16+ |
| 98 | ESTAT.HOUSEHOLDS.SINGLE | Single-person households |
| 171 | ESTAT.CO2.TRANSPORT | Transport CO2 emissions, domestic inventory |
| 179 | ESTAT.CO2.DOMESTIC.AVIATION | Domestic aviation CO2 emissions |

Interpretation: migrant stock is not annual migration; hotel arrivals are not unique visitors; alcohol data are provider estimates and may lag; ATM rates use adults; energy intensity uses constant 2021 PPP GDP; monetary current-price series are not inflation-adjusted. Transport and domestic aviation emissions exclude international bunkers. Life satisfaction is a 0–10 rating. Government revenue coverage follows World Bank metadata, not an assumed Eurostat general-government definition.

## Third batch — 3 October 2026: 48 additional indicators

Expands 108 to 156 indicators: 23 World Bank and 25 Eurostat measures, with at least one addition in every category. These were selected from the broader 814-series coverage screen; that screen includes variants, not 814 independent publication-ready KPIs. Each new measure carries its audit code and review date. All six country/EU slots use the existing refresh and provenance pipeline.

| Category | Added | Total |
| --- | ---: | ---: |
| Economy & productivity | 4 | 12 |
| Jobs & earnings | 5 | 8 |
| Public finances | 5 | 12 |
| Living standards & housing | 7 | 19 |
| Health & care | 4 | 12 |
| Education & research | 3 | 14 |
| Democracy, justice & rights | 2 | 11 |
| Population & migration | 3 | 17 |
| Environment & energy | 4 | 19 |
| Transport & infrastructure | 4 | 10 |
| Business & digital economy | 4 | 13 |
| Culture & tourism | 3 | 9 |

### Exact integration crosswalk

| Audit code | Public code | Indicator | Greek coverage |
| --- | --- | --- | --- |
| NE.GDI.FTOT.ZS | NE.GDI.FTOT.ZS | Fixed investment | 1974–2025, 52 observations |
| NY.GNS.ICTR.ZS | NY.GNS.ICTR.ZS | Gross savings | 1976–2024, 48 observations |
| NV.IND.MANF.ZS | NV.IND.MANF.ZS | Manufacturing value added | 1995–2025, 31 observations |
| BN.CAB.XOKA.GD.ZS | BN.CAB.XOKA.GD.ZS | Current account balance | 1976–2024, 48 observations |
| SL.EMP.TOTL.SP.ZS | SL.EMP.TOTL.SP.ZS | Employment-to-population ratio, ages 15+ | 1991–2025, 35 observations |
| SL.EMP.SELF.ZS | SL.EMP.SELF.ZS | Self-employment share | 1991–2025, 35 observations |
| SL.UEM.NEET.ZS | SL.UEM.NEET.ZS | Young people outside work, education or training | 1987–2025, 39 observations |
| SH.DYN.MORT | SH.DYN.MORT | Under-five mortality | 1974–2024, 51 observations |
| SH.XPD.OOPC.CH.ZS | SH.XPD.OOPC.CH.ZS | Out-of-pocket health spending | 2000–2023, 24 observations |
| SH.MED.PHYS.ZS | SH.MED.PHYS.ZS | Physicians per 1,000 people | 1974–2022, 47 observations |
| SH.DYN.NCOM.ZS | SH.DYN.NCOM.ZS | Premature mortality from four major NCDs | 2000–2021, 22 observations |
| SE.PRE.ENRR | SE.PRE.ENRR | Preprimary enrolment, gross | 1974–2020, 45 observations |
| SM.POP.NETM | SM.POP.NETM | Net migration | 1974–2025, 52 observations |
| SP.URB.GROW | SP.URB.GROW | Urban population growth | 1974–2025, 52 observations |
| EG.ELC.LOSS.ZS | EG.ELC.LOSS.ZS | Electricity transmission and distribution losses | 1990–2024, 35 observations |
| ER.H2O.FWST.ZS | ER.H2O.FWST.ZS | Water stress | 1974–2022, 49 observations |
| IS.RRS.GOOD.MT.K6 | IS.RRS.GOOD.MT.K6 | Rail freight | 1995–2021, 27 observations |
| IS.SHP.GOOD.TU | IS.SHP.GOOD.TU | Container port traffic | 2010–2024, 15 observations |
| IS.AIR.DPRT | IS.AIR.DPRT | Registered-carrier aircraft departures | 1974–2023, 50 observations |
| FS.AST.PRVT.GD.ZS | FS.AST.PRVT.GD.ZS | Domestic credit to private sector | 2001–2024, 24 observations |
| IC.BUS.NDNS.ZS | IC.BUS.NDNS.ZS | New business density | 2011–2024, 14 observations |
| TX.VAL.ICTG.ZS.UN | TX.VAL.ICTG.ZS.UN | ICT goods export share | 2000–2024, 25 observations |
| FB.CBK.BRCH.P5 | FB.CBK.BRCH.P5 | Commercial bank branch density | 2004–2024, 21 observations |
| ESTAT.NEW.01 | ESTAT.POVERTY.RISK | At risk of income poverty | 1995–2025, 30 observations |
| ESTAT.NEW.02 | ESTAT.POVERTY.AROPE | At risk of poverty or social exclusion | 2015–2025, 11 observations |
| ESTAT.NEW.03 | ESTAT.DEPRIVATION.SEVERE | Severe material and social deprivation | 2015–2025, 11 observations |
| ESTAT.NEW.04 | ESTAT.HOUSING.OVERCROWDING | Overcrowded housing | 2003–2025, 23 observations |
| ESTAT.NEW.05 | ESTAT.HOUSING.WARMTH | Unable to keep home adequately warm | 2003–2025, 23 observations |
| ESTAT.NEW.06 | ESTAT.HOUSEHOLDS.SIZE | Average household size | 2003–2025, 23 observations |
| ESTAT.NEW.07 | ESTAT.INCOME.MEDIAN | Median equivalised disposable income | 1995–2025, 30 observations |
| ESTAT.NEW.09 | ESTAT.EDUCATION.EARLY.LEAVERS | Early school leavers, ages 18–24 | 2000–2025, 26 observations |
| ESTAT.NEW.10 | ESTAT.EDUCATION.TERTIARY.ATTAINMENT | Tertiary attainment, ages 25–34 | 2000–2025, 26 observations |
| ESTAT.NEW.15 | ESTAT.HOTELS.NONRESIDENT.NIGHTS | Non-resident hotel nights | 1994–2025, 32 observations |
| ESTAT.NEW.16 | ESTAT.TOUR.TRIPS.ABROAD | Resident overnight trips abroad | 2012–2024, 13 observations |
| ESTAT.NEW.18 | ESTAT.JUSTICE.JUDGES | Professional judges | 2008–2024, 17 observations |
| ESTAT.NEW.20 | ESTAT.JUSTICE.PRISON.RATE | Prison population rate | 2008–2024, 17 observations |
| ESTAT.NEW.22 | ESTAT.MOTHERS.FIRST.AGE | Mean age at first childbirth | 1992–2024, 33 observations |
| ESTAT.NEW.24 | ESTAT.GOV.REVENUE | General government revenue | 1995–2025, 31 observations |
| ESTAT.NEW.25 | ESTAT.GOV.INTEREST | Government interest expenditure | 1995–2025, 31 observations |
| ESTAT.NEW.26 | ESTAT.GOV.SOCIAL.PROTECTION | Government social protection spending | 1995–2024, 30 observations |
| ESTAT.NEW.27 | ESTAT.GOV.CULTURE.RECREATION | Recreation, culture and religion spending | 1995–2024, 30 observations |
| ESTAT.NEW.28 | ESTAT.GOV.ENVIRONMENT | Government environmental protection spending | 1995–2024, 30 observations |
| ESTAT.NEW.29 | ESTAT.GOV.HOUSING | Housing and community amenities spending | 1995–2024, 30 observations |
| ESTAT.NEW.30 | ESTAT.RENEWABLES.TRANSPORT | Renewable energy in transport | 2004–2024, 21 observations |
| ESTAT.NEW.31 | ESTAT.RENEWABLES.HEATING | Renewable heating and cooling | 2004–2024, 21 observations |
| ESTAT.NEW.33 | ESTAT.CARS.ELECTRIC.REGISTRATIONS | New battery-electric car registrations | 2013–2025, 13 observations |
| ESTAT.NEW.39 | ESTAT.UNEMPLOYMENT.LONGTERM | Long-term unemployment rate | 2009–2025, 17 observations |
| ESTAT.SALARY.FTE | ESTAT.SALARY.FTE | Average annual full-time adjusted salary | 1995–2024, 30 observations |

### Interpretation and exclusions

Salary and median income are nominal euros, not inflation-adjusted purchasing power. Poverty and income years retain the provider’s survey-year labels; income commonly refers to the preceding year. AROPE uses the EU 2030 definition and is not spliced with the earlier definition. Electric-car registrations are explicitly labelled registrations, not the requested sales concept. Judges measure staffing, not judicial quality; prisoners are a stock, not a crime rate. COFOG GF08 includes recreation, sport and religion, not only culture. Preprimary enrolment and rail freight have older latest observations; the dashboard exposes their coverage and publication-lag warning.

No new WHO, OECD, NGO or scraped-source pipeline is activated by this batch. Historical-only, restricted, ambiguous and duplicate candidates remain outside it. Specialist culture and justice expansion needs further work. No government causality score is introduced.

Validation: every published observation is checked against the freshly retrieved raw response. Additional checks enforce the screened Greek/peer coverage, bilingual definitions, percentage-point versus absolute changes, and unique source slices. Existing chart, government-period and infographic tests run against the expanded dataset.
