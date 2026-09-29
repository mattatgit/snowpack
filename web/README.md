# 3D viewer

The viewer combines real Furanodake terrain with the first historical weather-forcing reconstruction and a lightweight land-cover layer.

## Current visual layers

- terrain;
- slope;
- aspect;
- recent snowfall age + 48-hour amount;
- hourly snowfall water equivalent;
- temperature;
- wind speed + animated flow streaks;
- slope-relative solar loading.

Scene context:

- ESA WorldCover tree-cover mask rendered as symbolic forest;
- moving sun object and matching directional light;
- labelled terrain features;
- camera-aware compass rose;
- adjustable vertical exaggeration.

## Resolution

These resolutions are intentionally separate:

- source terrain: GSI DEM5A, 5 m;
- terrain browser mesh: approximately 20 m;
- weather forcing/model: approximately 50 m;
- browser weather grid: approximately 50 m;
- source forest classification: ESA WorldCover, 10 m;
- symbolic tree placement: sampled from the browser terrain grid.

GSI DEM1A (1 m) has been probed at the Furanodake summit, study-area centre and four study-area corners and is available at all six samples. It is not yet used by the main terrain pipeline. A future terrain LOD pass can use DEM1A for close visual geometry without implying the weather/snow model itself has 1 m accuracy.

## Generate data

```bash
python -m pipeline.terrain.build_furanodake
python -m pipeline.terrain.probe_dem1a
python -m pipeline.weather.build_historical_forcing
python -m pipeline.terrain.export_web
python -m pipeline.terrain.export_features
python -m pipeline.landcover.worldcover
python -m pipeline.weather.export_web
```

Generated browser data live in `web/data/` and are not committed to Git.

## Run locally

From the repository root:

```bash
python -m http.server 8000
```

Open:

`http://localhost:8000/web/`

## Interpretation

The weather and snowfall layers are model forcing / visualisation, not observed snow-surface truth.

The recent-snow layer deliberately avoids photorealistic snow. Hue represents amount-weighted age of snowfall over the previous 48 hours (orange/new through red/violet to blue/cyan/older); colour strength represents accumulated snowfall water.

Wind remains a low-confidence input because valley AMeDAS wind is not a substitute for free-air/ridge wind. Animated wind streaks therefore illustrate the current v0 wind field rather than authoritative alpine flow.

The Giant Ridge and Nishi-shamen feature-label points are provisional label anchors based on documented route geography and should be refined during the design/geographic review pass.
