# Snowpack

An experiment in modelling and visualising mountain snow conditions.

Snowpack combines terrain, observed weather, forecast weather, snow physics, and field observations to estimate how snow is distributed across a mountain and how that distribution may change over the next hours and days.

The first proof of concept focuses on **Furanodake / Kamifuranodake, Hokkaido**.

## First milestone

Reconstruct a historical snow event around Furanodake from **31 December 2025 to 3 January 2026**, then compare the modelled snow distribution with real observations recorded by Japan Avalanche Network.

The first POC should:

- ingest a real Japanese DEM;
- derive slope, aspect, curvature and terrain exposure;
- ingest historical weather observations;
- estimate snowfall and simple wind redistribution;
- evolve an estimated snow state through time;
- export terrain + snow-state data for a browser-based 3D viewer;
- overlay observations separately from modelled data;
- preserve uncertainty/provenance for every layer.

## Product intent

This is a **snow forecasting and visualisation tool**, not a mountain-safety or route-safety system.

Future versions may display avalanche observations and low-confidence model-derived avalanche-related indicators, but the application must clearly distinguish:

1. measured observations;
2. trusted third-party observations;
3. interpolated values;
4. modelled estimates.

## Repository layout

```
docs/                         Architecture, data and modelling notes
pipeline/                     Data preparation and modelling code
  terrain/                    DEM and terrain-derived layers
  weather/                    Observations and forecast ingestion
  observations/               Field observation ingestion
  snow/                       Snow-state model
web/                          Future interactive 3D viewer
experiments/
  furanodake-2026-01/         Historical validation experiment
data/                         Local data conventions only; raw datasets are not committed
```

See [docs/architecture.md](docs/architecture.md) for the initial system design and [docs/data-sources.md](docs/data-sources.md) for candidate Japanese data sources.
