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
