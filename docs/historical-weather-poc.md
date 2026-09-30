# Furanodake historical weather forcing POC

## Period

The reconstruction begins at **2025-12-29 00:00 JST** and runs through **2026-01-04 00:00 JST**.

The original plan began on 31 December, but the Japan Avalanche Network bulletin for 3 January describes warming/rain through 29 December followed by 40–100 cm of snowfall, with the 31 December snow already settling. Starting on 29 December therefore gives the later snow-state model a defensible storm initialization period.

## Observations

Hourly JMA historical AMeDAS data are acquired for:

| Station | JMA historical block | AMeDAS ID | Elevation | Role |
| --- | --- | --- | ---: | --- |
| 上富良野 / Kamifurano | 1190 | 12596 | 220 m | temperature, precipitation, humidity, wind, sunshine |
| 富良野 / Furano | 0021 | 12626 | 174 m | temperature, precipitation, humidity, wind, sunshine, observed snowfall/snow depth |
| 白金 / Shirogane | 0020 | 12607 | 658 m | high-elevation-side precipitation gauge; other fields depend on station availability |

Official historical observations:

- https://www.data.jma.go.jp/stats/etrn/

The parsed source URL for every station/day is retained in `station-observations.csv`.

## Forcing grid

The first mountain forcing grid is approximately **50 m**.

It is derived from the 5 m terrain raster, not from the 20 m browser mesh. Weather forcing and terrain rendering are deliberately independent.

Dynamic hourly fields:

- temperature (°C);
- precipitation water equivalent (mm/h);
- estimated snowfall water equivalent (mm/h);
- eastward wind component (m/s);
- northward wind component (m/s);
- estimated slope-relative shortwave radiation (W/m²).

Static fields carried alongside the forcing:

- elevation;
- slope;
- aspect.

## Downscaling v0

This is intentionally a transparent first model.

### Temperature

Station temperature is adjusted to each terrain cell with a fixed lapse rate of **−6.5 °C/km**, then blended using inverse-distance weights.

This is a first-order approximation. Future versions should allow a time-varying lapse rate from model pressure levels or vertical observations.

### Precipitation

Observed hourly precipitation is spatially blended, then multiplied by a simple elevation enhancement:

- +40% per 1000 m above the locally weighted station elevation;
- multiplier clamped to 0.5–2.5.

This does **not** yet model wind-driven precipitation enhancement, gauge undercatch, or detailed orographic flow.

### Snow/rain phase

A deliberately simple temperature ramp is used:

- ≤ −1 °C: 100% snow;
- ≥ +2 °C: 0% snow;
- linear mixture in between.

### Wind

Observed AMeDAS wind vectors are blended spatially and wind speed is increased with elevation.

This is the weakest important part of v0.

Valley/station wind must **not** be interpreted as ridge wind. The 3 January JAN bulletin describes localized wind slabs at high elevation and cites a 2200 m forecast of WNW 11 m/s, so a free-air/mesoscale wind source is required before wind redistribution is treated seriously.

Likely next candidates:

- operational JMA LFM/MSM for forward forecasts;
- an appropriately licensed historical MSM/reanalysis source for reconstruction.

### Shortwave radiation

The v0 radiation field combines:

1. solar position from date/time/latitude;
2. cell slope and aspect;
3. JMA hourly sunshine fraction as a regional cloud proxy.

It currently omits:

- terrain-horizon shadowing;
- diffuse-sky radiation;
- atmospheric optical depth;
- reflected shortwave/albedo feedback;
- measured/modelled radiation flux.

This layer should therefore be treated as **relative terrain solar loading**, even though it is expressed as an approximate W/m² flux.

## Outputs

```text
data/processed/furanodake/weather/2025-12-29_2026-01-03/
  station-observations.csv
  forcing-summary.csv
  forcing-grid.npz
  forcing-meta.json
```

The NPZ contains the full hourly 50 m grids.

## Validation target

The first target is the JAN report that a wind-slab avalanche occurred on **1 January 2026** on steep **northeast-facing terrain on Furanodake's north ridge**.

The model should not be tuned simply to reproduce that result. Instead, the observation should be used to test whether independent meteorological forcing and terrain redistribution create enhanced loading in a physically compatible area.
