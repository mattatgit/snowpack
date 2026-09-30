# Furanodake terrain POC

## Study area

The first terrain build uses two nested WGS84 extents.

### Acquisition / model context

`142.58, 43.35, 142.70, 43.44` (west, south, east, north)

This is approximately 9.8 km east-west by 10.0 km north-south after projection. The extra terrain around the main riding area is intentional: later wind-redistribution calculations need surrounding terrain and should not run directly against the visible analysis boundary.

### Analysis / display area

`142.59, 43.36, 142.69, 43.43`

The initial extent contains:

- 富良野岳 / Furanodake — 1912 m;
- 上富良野岳 / Kamifuranodake — 1893 m;
- 上ホロカメットク山 / Kamihorokamettoku-yama — 1920 m;
- 十勝岳温泉 / Tokachidake Onsen trailhead area.

Peak coordinates are reference points, not substitutes for the DEM itself.

## Source

The POC acquires GSI elevation PNG tiles in this order:

1. `dem5a_png` — 5 m airborne-laser DEM;
2. `dem5b_png` — 5 m photogrammetric DEM;
3. `dem5c_png` — additional 5 m DEM product;
4. `dem_png` — 10 m DEM fallback.

Official documentation:

- https://maps.gsi.go.jp/development/ichiran.html
- https://maps.gsi.go.jp/development/demtile.html

The 5 m products are requested at XYZ zoom 15. Missing cells are filled from DEM10B at zoom 14. The build writes a source-quality raster so downstream modelling can distinguish DEM5A/B/C from fallback terrain.

The original GSI raster resolution and the XYZ tile sampling resolution are not treated as equivalent. The tile service is an acquisition format; the source-quality layer records which source product contributed each cell.

## Exact XYZ tile ranges

For the acquisition bounding box:

### DEM5

- zoom: 15
- x: 29361–29372
- y: 11985–11996
- maximum tiles: 144

Each tile is attempted in source-quality order DEM5A → DEM5B → DEM5C.

### DEM10 fallback

- zoom: 14
- x: 14680–14686
- y: 5992–5998
- tiles: 49

Actual source usage is captured at build time in metadata and `source-quality.tif`.

## Projection and grid

Working CRS: **JGD2011 / Japan Plane Rectangular CS XII — EPSG:6680**.

Working cell size: **5 m**.

Current projected grid:

- width: 1955 cells;
- height: 2009 cells;
- total: 3,927,595 cells;
- approximate dimensions: 9,775 × 10,045 m.

The 5 m working grid is deliberately finer than the eventual snow-physics grid. We expect the first snow simulation to aggregate terrain to approximately 20–50 m.

## Outputs

Running the terrain builder creates:

```text
data/processed/furanodake/terrain/
  elevation.tif
  slope-degrees.tif
  aspect-degrees.tif
  source-quality.tif
  gsi-tile-manifest.json
  metadata.json
```

`source-quality.tif` codes:

- 0 — nodata;
- 1 — GSI DEM5A;
- 2 — GSI DEM5B;
- 3 — GSI DEM5C;
- 4 — GSI DEM10B fallback.

## Run

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pipeline.terrain.build_furanodake
```

Raw downloaded tiles are cached beneath `data/raw/gsi/`. Generated rasters live beneath `data/processed/`; both are ignored by Git.

## Attribution

Derived outputs should retain the GSI attribution used in `metadata.json`:

> 地理院タイル（標高タイル（基盤地図情報数値標高モデル））を加工して作成

Before production/public redistribution, re-check the current GSI content terms and whether the intended use requires a Survey Act procedure.
