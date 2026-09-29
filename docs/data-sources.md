# Candidate data sources

This document tracks likely sources for the Furanodake proof of concept. Licensing, redistribution rights, operational access and exact coverage must be verified before production use.

## Terrain

### Geospatial Information Authority of Japan (GSI / 国土地理院)

Candidate source for:

- DEM / elevation;
- map reference data;
- potentially 1 m, 5 m or 10 m terrain depending on local coverage.

Official entry points:

- https://www.gsi.go.jp/
- https://service.gsi.go.jp/kiban/

POC questions:

- What is the highest-quality DEM available over the complete Furanodake/Kamifuranodake test extent?
- Is the best source bare-earth LiDAR-derived DEM or photogrammetry?
- What derived-data attribution is required?

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

Candidate sources:

- Ministry of the Environment vegetation GIS;
- MLIT land-use datasets;
- possibly satellite-derived land cover.

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
