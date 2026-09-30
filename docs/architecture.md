# Architecture

## Goal

Build a mountain-scale snow-state model that can ingest current conditions and weather forecasts, evolve the snow state through time, and render the result as a rotatable 3D terrain model.

The first implementation is deliberately modular so that simple modelling can later be replaced or compared with packages such as SNOWPACK / Alpine3D or FSM2.

## Initial processing flow

```
GSI DEM
   |
   v
Terrain preprocessing
   |- elevation
   |- slope
   |- aspect
   |- curvature
   |- terrain exposure / shelter
   |- solar geometry
   v
Mountain grid
   ^
   |
Observed weather --------+
Forecast weather --------+--> Weather downscaling
                         |       |- lapse-rate temperature
Field observations ------+       |- precipitation phase
                                 |- terrain-adjusted wind
                                 |- radiation / shading
                                         |
                                         v
                                  Snow-state model
                                         |
                         +---------------+----------------+
                         |                                |
                         v                                v
                  State snapshots                 Confidence/provenance
                         |
                         v
                  Browser-ready dataset
                         |
                         v
                    3D viewer
```

## Core principle: state, not a static snow-depth map

Each terrain cell should carry both fixed terrain properties and time-varying snow state.

### Static terrain

- elevation;
- slope;
- aspect;
- curvature / terrain shape;
- vegetation class;
- terrain shelter / wind exposure;
- horizon / solar geometry.

### Snow state

Initial POC:

- estimated snow depth;
- snow-water equivalent;
- new snow;
- bulk density;
- surface temperature;
- wind deposition / erosion accumulator;
- time since snowfall.

Later:

- multilayer stratigraphy;
- grain type / metamorphism;
- liquid water content;
- melt/refreeze state;
- crust state.

### Confidence and provenance

Every output should retain enough metadata to answer:

- Was this measured, interpolated or modelled?
- Which source/run produced it?
- How far is it from an observation?
- What model version produced the value?
- When was it last updated?

## Proposed stack

### Data/model pipeline

Python is the initial choice because its geospatial/scientific ecosystem is strong and interoperates well with the snow models we may later evaluate.

Likely packages:

- NumPy
- xarray
- rasterio / rioxarray
- pyproj
- pandas
- scipy

Dependencies should be added only when needed.

### Viewer

A separate browser viewer will probably use Three.js. The model pipeline should therefore export ordinary portable formats rather than couple itself to the frontend.

Candidate outputs:

- terrain mesh / glTF;
- Cloud Optimized GeoTIFF for raster layers;
- compact binary grids for time-varying state;
- GeoJSON for observations.

## Resolution

Keep three resolutions conceptually separate:

1. **source terrain resolution** — potentially 1–10 m;
2. **model grid resolution** — likely 20–50 m for the first POC;
3. **render resolution** — chosen for visual quality/performance.

Running a physical snow model at the finest available DEM resolution would imply false precision and unnecessary computation.

## Historical validation experiment

First target:

- Furanodake / Kamifuranodake;
- 31 Dec 2025–3 Jan 2026;
- reconstruct weather forcing;
- compare simulated redistribution with known field observations;
- especially inspect lee loading / scouring patterns.

This historical reconstruction should work before live forecasts are added.

## Safety / communication rule

The application must not collapse uncertain simulations into authoritative safety judgements.

Avalanche-related information should be presented as separate layers:

- official/structured observation;
- community observation;
- model-derived indicator;
- model confidence.

No model layer should be labelled “safe” or “unsafe”.
