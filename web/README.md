# 3D viewer

The viewer now combines the real Furanodake terrain with the first historical weather-forcing reconstruction.

It supports:

- orbit / zoom / pan;
- terrain, slope and aspect layers;
- historical temperature;
- hourly snowfall water equivalent;
- wind speed;
- slope-relative solar loading;
- 144-hour time slider for 29 Dec 2025 through 3 Jan 2026;
- adjustable vertical exaggeration;
- source attribution and explicit wind/solar confidence notes.

## Generate data

Build terrain and weather first:

```bash
python -m pipeline.terrain.build_furanodake
python -m pipeline.weather.build_historical_forcing
python -m pipeline.terrain.export_web
python -m pipeline.weather.export_web
```

The static terrain render grid is 20 m. Historical weather is exported at approximately 100 m for browser performance; the underlying forcing model remains approximately 50 m.

Generated browser data live in `web/data/` and are not committed to Git.

## Run locally

From the repository root:

```bash
python -m http.server 8000
```

Open:

`http://localhost:8000/web/`

## Interpretation

The historical weather layers are **forcing inputs**, not yet simulated snowpack.

Temperature and precipitation use transparent terrain downscaling from JMA observations. Wind is deliberately labelled low-confidence because valley AMeDAS wind is not a substitute for free-air/ridge wind. Solar is a relative terrain-loading estimate rather than a complete radiative-transfer calculation.
