# Candidate data sources

This document tracks likely sources for the Furanodake proof of concept. Licensing, redistribution rights, operational access and exact coverage must be verified before production use.

## Terrain

### Geospatial Information Authority of Japan (GSI / 国土地理院)

Candidate source for:

- DEM / elevation;
- map reference data;
- 1 m, 5 m or 10 m terrain depending on local coverage.

Official entry points:

- https://www.gsi.go.jp/
- https://service.gsi.go.jp/kiban/

Current POC result:

- GSI DEM5A covers the Furanodake study area and is the modelling terrain source;
- DEM1A probes at the summit, study centre and four study-area corners all returned valid coverage;
- the focused browser viewer now renders the DEM5A terrain at 5 m;
- DEM1A should be tested later as a close-range level-of-detail source rather than implying 1 m weather/snow-model accuracy.

## Weather observations and forecasts

### Japan Meteorological Agency (JMA / 気象庁)

Candidate inputs:

- AMeDAS observations;
- precipitation;
- temperature;
- wind;
- snow depth where measured;
- radar precipitation analysis;
- Local Forecast Model (LFM);
- Meso-Scale Model (MSM);
- Global Spectral Model (GSM).

Official developer/data information:

- https://www.data.jma.go.jp/developer/

Likely POC use:

- observations to reconstruct historical forcing;
- radar/analysis to improve precipitation spatial distribution;
- LFM for short-range forecasts;
- MSM for roughly day-1 to day-3 forecasts;
- GSM only for longer-range trend guidance.

Production access should use an appropriate supported distribution route rather than scrape presentation pages.

### JMA Radar/Raingauge-Analyzed Precipitation (解析雨量)

This is the preferred next upgrade to the historical precipitation field.

JMA describes the product as a combination of weather radar and surface rain gauges, analysed as previous-one-hour precipitation on a 1 km grid over Japan. The standard analysis is produced every 30 minutes. The operational GRIB2 filename pattern is:

`Z__C_RJTD_yyyyMMddhhmmss_SRF_GPV_Ggis1km_Prr60lv_ANAL_grib2.bin`

Important implications for Snowpack:

- it should provide much better storm-scale spatial structure than interpolation from three AMeDAS stations;
- 1 km remains much coarser than the 5 m terrain, so fine-scale snow differences must come from terrain/elevation, precipitation-phase and later wind-redistribution modelling rather than pretending the observation itself is high resolution;
- the analysed precipitation field can be downscaled onto the snow grid using terrain-aware modifiers while retaining the original 1 km provenance/confidence;
- the standard analysed product should be preferred over the faster 10-minute preliminary analysis where historical accuracy matters, because the standard product uses more rain gauges.

Historical access is a separate acquisition problem from the public presentation tiles. JMBSC documents archived analysed-precipitation datasets and JMA's cloud/data-distribution systems; these should be used rather than relying on undocumented tile scraping. For the 29 Dec 2025–3 Jan 2026 validation period we need to obtain the GRIB2 archive, crop the Hokkaido/Furanodake grid and compare it against the current AMeDAS-derived precipitation reconstruction.

## Avalanche / field observations

### Japan Avalanche Network (JAN)

Candidate source for structured avalanche and snow observations, including Daisetsu / Tokachi.

- https://data.nadare.jp/

This is especially valuable for historical validation because model output can be compared against observations independently recorded in the field.

Keep JAN records as an observation layer; do not turn them into model truth without preserving source and timestamp.

## Community observations

### Instagram / other public social sources

Potential supplementary observations:

- fresh snowfall;
- wind effect;
- crust;
- powder preservation;
- avalanche debris;
- cracking/cornices;
- qualitative visibility/surface condition.

These should be lower-confidence than structured professional observations unless independently verified.

Important implementation questions:

- API eligibility and hashtag-search limitations;
- location ambiguity;
- timestamp vs observation time;
- duplicate/cross-post handling;
- whether content/licensing terms permit derived structured observations.

## Vegetation / land cover

Current POC source:

- ESA WorldCover 2021 v200, 10 m tree-cover class.

Future candidate:

- JAXA high-resolution land-cover products for Japan, which can distinguish forest types more usefully than a binary tree-cover mask.

Use case:

- forest/open-alpine classification;
- canopy interception;
- wind shelter;
- radiation.

## Snow-model candidates

### Simple Snowpack model (our POC)

First build should remain transparent and inspectable:

```
precipitation
+ precipitation phase
+ elevation adjustment
+ temperature history
+ settling
+ solar exposure
+ wind erosion/deposition
= evolving estimated snow state
```

Purpose: validate the data pipeline and terrain behaviour before adding a complex external model.

### SNOWPACK / Alpine3D

- https://snowpack.slf.ch/
- https://alpine3d.slf.ch/

Candidate for later comparison / higher-fidelity snow physics and spatial modelling.

### FSM2

- https://github.com/RichardEssery/FSM2

Candidate lightweight/open snow-energy model for comparison.

## Data policy

Raw third-party datasets should not be committed to Git.

For every imported dataset we should record:

- provider;
- product name;
- source URL;
- licence/terms;
- acquisition timestamp;
- spatial/temporal resolution;
- original CRS;
- bounding box;
- processing steps;
- checksum where practical.
