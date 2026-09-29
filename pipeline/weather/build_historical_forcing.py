from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.transform import Affine

from pipeline.terrain.build_furanodake import terrain_derivatives
from pipeline.weather.jma_history import fetch_station_period, wind_components


def resampled_elevation(
    path: Path, target_resolution_m: float
) -> tuple[np.ndarray, Affine, str]:
    with rasterio.open(path) as dataset:
        source_resolution = abs(dataset.transform.a)
        scale = source_resolution / target_resolution_m
        width = max(2, int(round(dataset.width * scale)))
        height = max(2, int(round(dataset.height * scale)))
        elevation = dataset.read(
            1,
            out_shape=(height, width),
            resampling=Resampling.bilinear,
        ).astype(np.float32)
        transform = dataset.transform * Affine.scale(
            dataset.width / width, dataset.height / height
        )
        return elevation, transform, dataset.crs.to_string()


def cell_centres(transform: Affine, width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    columns = np.arange(width, dtype=np.float64) + 0.5
    rows = np.arange(height, dtype=np.float64) + 0.5
    x = transform.c + columns * transform.a
    y = transform.f + rows * transform.e
    return np.meshgrid(x, y)


def station_weight_grids(
    stations: list[dict],
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    crs: str,
    softening_m: float = 2000.0,
) -> np.ndarray:
    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    grids: list[np.ndarray] = []
    for station in stations:
        x, y = transformer.transform(float(station["lon"]), float(station["lat"]))
        distance_sq = (x_grid - x) ** 2 + (y_grid - y) ** 2
        grids.append(1.0 / (distance_sq + softening_m**2))
    return np.stack(grids).astype(np.float64)


def weighted_field(
    values: np.ndarray,
    weight_grids: np.ndarray,
    fallback: float = math.nan,
) -> np.ndarray:
    valid = np.isfinite(values)
    if not np.any(valid):
        return np.full(weight_grids.shape[1:], fallback, dtype=np.float32)
    weighted = weight_grids[valid] * values[valid, None, None]
    denom = np.sum(weight_grids[valid], axis=0)
    return (np.sum(weighted, axis=0) / denom).astype(np.float32)


def solar_position(
    timestamp: datetime,
    latitude_deg: float,
    longitude_deg: float,
) -> tuple[float, float]:
    """Approximate solar altitude/azimuth. Azimuth is clockwise from north."""
    local = timestamp
    day_of_year = local.timetuple().tm_yday
    hour = local.hour + local.minute / 60 + local.second / 3600
    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour - 12.0) / 24.0)

    equation_minutes = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    declination = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )

    offset_hours = local.utcoffset().total_seconds() / 3600.0 if local.utcoffset() else 0.0
    time_offset_minutes = equation_minutes + 4.0 * longitude_deg - 60.0 * offset_hours
    true_solar_minutes = hour * 60.0 + time_offset_minutes
    hour_angle = math.radians(true_solar_minutes / 4.0 - 180.0)

    latitude = math.radians(latitude_deg)
    sin_altitude = (
        math.sin(latitude) * math.sin(declination)
        + math.cos(latitude) * math.cos(declination) * math.cos(hour_angle)
    )
    altitude = math.asin(max(-1.0, min(1.0, sin_altitude)))

    azimuth = math.atan2(
        math.sin(hour_angle),
        math.cos(hour_angle) * math.sin(latitude)
        - math.tan(declination) * math.cos(latitude),
    )
    azimuth = (azimuth + math.pi) % (2.0 * math.pi)
    return altitude, azimuth


def slope_shortwave(
    timestamp: datetime,
    slope_deg: np.ndarray,
    aspect_deg: np.ndarray,
    sunshine_fraction: float,
    latitude_deg: float,
    longitude_deg: float,
) -> np.ndarray:
    altitude, azimuth = solar_position(timestamp, latitude_deg, longitude_deg)
    if altitude <= 0:
        return np.zeros_like(slope_deg, dtype=np.float32)

    slope = np.deg2rad(slope_deg)
    aspect = np.deg2rad(aspect_deg)
    incidence = (
        math.sin(altitude) * np.cos(slope)
        + math.cos(altitude) * np.sin(slope) * np.cos(azimuth - aspect)
    )
    incidence = np.maximum(incidence, 0.0)

    sunshine_fraction = float(np.clip(sunshine_fraction, 0.0, 1.0))
    cloud_factor = 0.25 + 0.75 * sunshine_fraction
    # Deliberately simple v0 estimate: approximately 900 W/m² at normal incidence
    # under clear winter sky, reduced by JMA estimated sunshine fraction.
    return (900.0 * incidence * cloud_factor).astype(np.float32)


def snow_fraction_from_temperature(temperature_c: np.ndarray) -> np.ndarray:
    """Simple mixed-phase ramp: all snow <= -1 C, all rain >= 2 C."""
    return np.clip((2.0 - temperature_c) / 3.0, 0.0, 1.0).astype(np.float32)


def circular_direction(u: float, v: float) -> float:
    if not math.isfinite(u) or not math.isfinite(v) or math.hypot(u, v) < 1e-6:
        return math.nan
    return (math.degrees(math.atan2(-u, -v)) + 360.0) % 360.0


def run(
    terrain_root: Path,
    weather_config_path: Path,
    output_root: Path,
) -> None:
    config = json.loads(weather_config_path.read_text(encoding="utf-8"))
    timezone_name = config["timezone"]
    timezone = ZoneInfo(timezone_name)
    start = datetime.fromisoformat(config["period_start"]).astimezone(timezone)
    end = datetime.fromisoformat(config["period_end"]).astimezone(timezone)
    resolution_m = float(config["forcing_resolution_m"])
    stations = config["stations"]

    output_root.mkdir(parents=True, exist_ok=True)
    station_frames: list[pd.DataFrame] = []
    for station in stations:
        frame = fetch_station_period(station, start, end, timezone_name)
        station_frames.append(frame)
    observations = pd.concat(station_frames, ignore_index=True)
    observations.to_csv(output_root / "station-observations.csv", index=False)

    elevation, transform, crs = resampled_elevation(
        terrain_root / "elevation.tif", resolution_m
    )
    height, width = elevation.shape
    slope, aspect = terrain_derivatives(elevation, abs(transform.a))
    x_grid, y_grid = cell_centres(transform, width, height)
    weights = station_weight_grids(stations, x_grid, y_grid, crs)
    station_elevations = np.asarray(
        [float(station["elevation_m"]) for station in stations], dtype=np.float64
    )
    blended_station_elevation = weighted_field(station_elevations, weights)

    timestamps = sorted(observations["time_end_jst"].unique())
    expected_hours = int((end - start).total_seconds() // 3600)
    if len(timestamps) != expected_hours:
        raise ValueError(
            f"Expected {expected_hours} forcing hours, found {len(timestamps)}"
        )

    shape = (len(timestamps), height, width)
    temperature = np.empty(shape, dtype=np.float32)
    snowfall_water = np.empty(shape, dtype=np.float32)
    precipitation = np.empty(shape, dtype=np.float32)
    wind_u = np.empty(shape, dtype=np.float32)
    wind_v = np.empty(shape, dtype=np.float32)
    shortwave = np.empty(shape, dtype=np.float32)

    lapse_rate = float(config["temperature_lapse_rate_c_per_m"])
    precip_rate = float(config["precip_orographic_rate_per_1000m"])
    wind_rate = float(config["wind_speed_increase_per_1000m"])

    station_names = [station["name"] for station in stations]
    centre_lat = float(np.mean([station["lat"] for station in stations]))
    centre_lon = float(np.mean([station["lon"] for station in stations]))

    summaries: list[dict[str, object]] = []
    for index, timestamp_text in enumerate(timestamps):
        rows = observations.loc[observations["time_end_jst"] == timestamp_text].set_index(
            "station_name"
        ).reindex(station_names)

        station_temp = rows["temperature_c"].to_numpy(dtype=np.float64)
        temp_candidates = np.stack(
            [
                np.full_like(elevation, value, dtype=np.float32)
                + lapse_rate * (elevation - station_elevations[i])
                if math.isfinite(value)
                else np.full_like(elevation, np.nan, dtype=np.float32)
                for i, value in enumerate(station_temp)
            ]
        )
        valid_temp = np.isfinite(station_temp)
        if not np.any(valid_temp):
            raise ValueError(f"No station temperature at {timestamp_text}")
        temp_weights = weights[valid_temp]
        temperature[index] = (
            np.sum(temp_candidates[valid_temp] * temp_weights, axis=0)
            / np.sum(temp_weights, axis=0)
        )

        station_precip = rows["precipitation_mm"].to_numpy(dtype=np.float64)
        base_precip = weighted_field(station_precip, weights, fallback=0.0)
        orographic_factor = np.clip(
            1.0
            + precip_rate
            * ((elevation - blended_station_elevation) / 1000.0),
            0.5,
            2.5,
        ).astype(np.float32)
        precipitation[index] = np.maximum(base_precip, 0.0) * orographic_factor
        snowfall_water[index] = precipitation[index] * snow_fraction_from_temperature(
            temperature[index]
        )

        speed = rows["wind_speed_m_s"].to_numpy(dtype=np.float64)
        direction = rows["wind_direction_deg"].to_numpy(dtype=np.float64)
        calm = np.isfinite(speed) & (speed <= 0.2) & ~np.isfinite(direction)
        u, v = wind_components(speed, direction)
        u[calm] = 0.0
        v[calm] = 0.0
        base_u = weighted_field(u, weights, fallback=0.0)
        base_v = weighted_field(v, weights, fallback=0.0)
        wind_factor = np.clip(
            1.0
            + wind_rate
            * ((elevation - blended_station_elevation) / 1000.0),
            0.6,
            1.8,
        ).astype(np.float32)
        wind_u[index] = base_u * wind_factor
        wind_v[index] = base_v * wind_factor

        sunshine = rows["sunshine_hours"].to_numpy(dtype=np.float64)
        sunshine_valid = np.isfinite(sunshine)
        if np.any(sunshine_valid):
            sunshine_grid = weighted_field(sunshine, weights, fallback=0.0)
            sunshine_fraction = float(np.nanmean(sunshine_grid))
        else:
            sunshine_fraction = 0.0

        midpoint = datetime.fromisoformat(
            rows["time_mid_jst"].dropna().iloc[0]
        ).astimezone(timezone)
        shortwave[index] = slope_shortwave(
            midpoint,
            slope,
            aspect,
            sunshine_fraction,
            centre_lat,
            centre_lon,
        )

        mean_u = float(np.nanmean(wind_u[index]))
        mean_v = float(np.nanmean(wind_v[index]))
        summaries.append(
            {
                "time_end_jst": timestamp_text,
                "temperature_mean_c": float(np.nanmean(temperature[index])),
                "temperature_min_c": float(np.nanmin(temperature[index])),
                "temperature_max_c": float(np.nanmax(temperature[index])),
                "precipitation_mean_mm": float(np.nanmean(precipitation[index])),
                "snowfall_water_mean_mm": float(np.nanmean(snowfall_water[index])),
                "wind_speed_mean_m_s": float(
                    np.nanmean(np.hypot(wind_u[index], wind_v[index]))
                ),
                "wind_direction_mean_deg": circular_direction(mean_u, mean_v),
                "shortwave_mean_w_m2": float(np.nanmean(shortwave[index])),
                "shortwave_max_w_m2": float(np.nanmax(shortwave[index])),
                "sunshine_fraction": sunshine_fraction,
            }
        )

    np.savez_compressed(
        output_root / "forcing-grid.npz",
        elevation_m=elevation.astype(np.float32),
        slope_deg=slope.astype(np.float32),
        aspect_deg=aspect.astype(np.float32),
        temperature_c=temperature,
        precipitation_mm=precipitation,
        snowfall_water_mm=snowfall_water,
        wind_u_m_s=wind_u,
        wind_v_m_s=wind_v,
        shortwave_w_m2=shortwave,
    )
    pd.DataFrame(summaries).to_csv(output_root / "forcing-summary.csv", index=False)

    metadata = {
        "generated_at_utc": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "timezone": timezone_name,
        "hours": len(timestamps),
        "timestamps_end_jst": timestamps,
        "grid": {
            "crs": crs,
            "resolution_m": abs(transform.a),
            "width": width,
            "height": height,
            "transform": list(transform)[:6],
        },
        "stations": stations,
        "model": {
            "temperature": {
                "method": "inverse-distance station interpolation plus fixed elevation lapse rate",
                "lapse_rate_c_per_m": lapse_rate,
            },
            "precipitation": {
                "method": "inverse-distance station precipitation plus simple elevation multiplier",
                "orographic_rate_per_1000m": precip_rate,
                "factor_limits": [0.5, 2.5],
            },
            "snow_phase": {
                "method": "linear temperature ramp",
                "all_snow_at_or_below_c": -1.0,
                "all_rain_at_or_above_c": 2.0,
            },
            "wind": {
                "method": "inverse-distance observed valley wind vectors plus elevation speed multiplier",
                "speed_increase_per_1000m": wind_rate,
                "factor_limits": [0.6, 1.8],
                "warning": "Does not yet represent free-air/ridge wind or terrain flow acceleration/shelter.",
            },
            "shortwave": {
                "method": "solar geometry on slope/aspect scaled by JMA sunshine fraction",
                "clear_normal_reference_w_m2": 900.0,
                "minimum_cloud_factor": 0.25,
                "warning": "No horizon shading, diffuse-radiation model, atmospheric column or measured radiation yet.",
            },
        },
        "provenance": {
            "observations": "Japan Meteorological Agency historical AMeDAS hourly pages",
            "terrain": "GSI-derived terrain pipeline output",
        },
    }
    (output_root / "forcing-meta.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Fetched {len(observations):,} station-hour rows")
    print(
        f"Built {len(timestamps)} hours on {width} x {height} grid "
        f"({width * height:,} cells/hour) at {abs(transform.a):g} m"
    )
    print(f"Wrote {output_root}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build historical Furanodake weather forcing from JMA observations"
    )
    parser.add_argument(
        "--terrain-root",
        type=Path,
        default=Path("data/processed/furanodake/terrain"),
    )
    parser.add_argument(
        "--weather-config",
        type=Path,
        default=Path("config/furanodake-weather.json"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/processed/furanodake/weather/2025-12-31_2026-01-03"),
    )
    args = parser.parse_args()
    run(args.terrain_root, args.weather_config, args.output_root)
